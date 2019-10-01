import sqlite3
import time
from unittest import mock
import uuid

import pytest

from conductor_searchcounter import dao
from conductor_searchcounter import counter
from conductor_searchcounter import utils


SECONDS_NOW = 1569887365
NANOSECONDS_NOW = utils.seconds_in_nano(SECONDS_NOW)


@pytest.fixture(params=["list", "sqlite"])
def empty_daolist(request):
    if request.param == "sqlite":
        conn = sqlite3.connect(":memory:")
        d = dao.DAOSqlite(conn)
    else:
        d = dao.DAOList()

    yield d

    if request.param == 'sqlite':
        conn.close()


@pytest.fixture(params=["list", "sqlite"])
def daolist(request):
    if request.param == "sqlite":
        conn = sqlite3.connect(":memory:")
        d = dao.DAOSqlite(conn)
    else:
        d = dao.DAOList()

    s = create_search("term3", utils.seconds_in_nano(SECONDS_NOW - 5))
    d.append(s)

    for i in range(3, 0, -1):
        term = f"term{i}"
        s = create_search(term, utils.seconds_in_nano(SECONDS_NOW - i))
        d.append(s)

    yield d

    if request.param == 'sqlite':
        conn.close()


@pytest.fixture
def search1():
    return create_search("search1", utils.seconds_in_nano(SECONDS_NOW))


@pytest.fixture
def search2():
    return create_search("search2", utils.seconds_in_nano(SECONDS_NOW + 1))


def create_search(search_term, search_timestamp=None):
    if search_timestamp is None:
        search_timestamp = time.time_ns()

    search_id = uuid.uuid4()

    return counter.Search(search_id, search_term, search_timestamp)


@mock.patch("time.time_ns")
def test_daolist_append(mock_time, empty_daolist, search1, search2):
    mock_time.return_value = NANOSECONDS_NOW

    empty_daolist.append(search1)
    assert empty_daolist.num_arbitrary_lookback(60) == 1

    empty_daolist.append(search2)
    assert empty_daolist.num_arbitrary_lookback(60) == 2


@mock.patch("time.time_ns")
def test_num_arbitrary_lookback(mock_time, daolist):
    mock_time.return_value = NANOSECONDS_NOW

    assert daolist.num_arbitrary_lookback(1) == 1
    assert daolist.num_arbitrary_lookback(2) == 2
    assert daolist.num_arbitrary_lookback(3) == 3
    assert daolist.num_arbitrary_lookback(4) == 3
    assert daolist.num_arbitrary_lookback(5) == 4


@mock.patch("time.time_ns")
def test_most_common_term(mock_time, daolist):
    mock_time.return_value = NANOSECONDS_NOW

    assert daolist.most_common_term(1) == "term1"
    assert daolist.most_common_term(5) == "term3"


def test_dao_interface_not_implmented_methods(search1):
    d = dao.DAO()

    with pytest.raises(NotImplementedError):
        d.append(search1)

    with pytest.raises(NotImplementedError):
        d.num_arbitrary_lookback(1)

    with pytest.raises(NotImplementedError):
        d.most_common_term(1)
