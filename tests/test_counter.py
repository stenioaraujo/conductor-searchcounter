from unittest import mock
import uuid

import pytest

from conductor_searchcounter import counter
from conductor_searchcounter import utils


SECONDS_NOW = 1569887365
NANOSECONDS_NOW = utils.seconds_in_nano(SECONDS_NOW)


@pytest.fixture
def searchcounter():
    terms = [f'term{i}' for i in range(3)]
    return counter.SearchCounter(terms)


def subtract_seconds(subtract_sec=0, nanosec=NANOSECONDS_NOW):
    subtract_nanoseconds = utils.seconds_in_nano(subtract_sec)
    return nanosec - subtract_nanoseconds


def test_create_search():
    search_id = uuid.uuid4()
    search_term = "term"
    search_timestamp = NANOSECONDS_NOW

    search = counter.Search(search_id, search_term, search_timestamp)

    assert search.id == search_id
    assert search.term == search_term
    assert search.timestamp == search_timestamp


def test_increment(searchcounter):
    sc = searchcounter

    sc.increment()
    assert len(sc._dao._search_history) == 1

    sc.increment()
    assert len(sc._dao._search_history) == 2


@mock.patch("time.time_ns")
def test_num_last_minute(mock_time, searchcounter):
    sc = searchcounter

    mock_time.return_value = subtract_seconds(61)
    sc.increment()

    mock_time.return_value = subtract_seconds(30)
    sc.increment()

    mock_time.return_value = subtract_seconds()
    sc.increment()

    assert sc.num_last_minute() == 2


@mock.patch("random.choice")
@mock.patch("time.time_ns")
def test_most_common_term(mock_time, mock_random):
    terms = ["term0", "term1", "term2"]
    term_choices = [terms[i] for i in (0, 0, 2, 1, 0, 1)]
    timestamps = [
        subtract_seconds(i) for i in range(len(term_choices) - 1, -1, -1)]

    mock_random.side_effect = term_choices
    mock_time.side_effect = timestamps

    sc = counter.SearchCounter(terms)
    for _ in range(len(timestamps)):
        sc.increment()

    mock_time.side_effect = [NANOSECONDS_NOW] * len(timestamps)
    assert sc.most_common_term(1) == "term0"
    assert sc.most_common_term(2) == "term1"
    assert sc.most_common_term(3) == "term1"
    assert sc.most_common_term(4) == "term0"
    assert sc.most_common_term(5) == "term0"
