import bisect
from collections import Counter
import time

from conductor_searchcounter import utils
from conductor_searchcounter import counter


class DAO:
    def append(self, search):
        raise NotImplementedError

    def num_arbitrary_lookback(self, seconds):
        raise NotImplementedError

    def most_common_term(self, seconds):
        raise NotImplementedError


class DAOList(DAO):
    def __init__(self):
        self._search_history = []

    def append(self, search):
        """Add search to search history

        :param search: (counter.Search) the search object to be added
        """
        self._search_history.append(search)

    def num_arbitrary_lookback(self, seconds):
        """Return the number of searches made in the past seconds

        :param seconds: (int) The number of seconds in the past
        :returns: (int) The number of searches
        """
        offset = self._get_offset(seconds)

        return len(self._search_history) - offset

    def _get_offset(self, seconds):
        """Get the offset index in the search history that matches seconds

        It returns an offset index in the search history that matches
        the first search in the interval [now - seconds, now], now
        is calculated by using time.time_ns().

        :param seconds: (int) The number of seconds in the past
        :returns: (int) The offset
        """
        now_nanosec = time.time_ns()
        target_nanosec = now_nanosec - utils.seconds_in_nano(seconds)
        target_search = counter.Search(None, None, target_nanosec)

        offset = bisect.bisect_left(self._search_history, target_search)

        return offset

    def most_common_term(self, seconds):
        """Return the most commonly searched term in the past seconds

        :param seconds: (int) The number of seconds in the past
        :returns: (int) The most commonly searched term
        """
        offset = self._get_offset(seconds)

        counter = Counter()
        for search in self._search_history[offset:]:
            counter[search.term] += 1

        most_common = counter.most_common(1)
        if most_common:
            return most_common[0][0]


class DAOSqlite(DAO):
    def __init__(self, conn):
        """Create an instance of DAO that can be used with a SQLite DB

        :param conn: (Connection) The connection object that represents the
            database
        """
        self._table_name = "search_history"
        self._conn = conn
        self._cursor = conn.cursor()

        self._initialize()

    def _initialize(self):
        """Create the table and index to store the searches

        If the database doesn't have the table to store the searches,
        it creates the table with the needed columns. It also creates an
        index on the column `timestamp`, so the filter operations can be done
        using binary search O(log(n))

        :raises: sqlite3.DatabaseError if the database is not valid
        """
        query_table = self._cursor.execute(f"""
            SELECT name
            FROM sqlite_master
            WHERE type='table' AND name='{self._table_name}';""")

        if not query_table.fetchone():
            self._cursor.execute(f"""
                CREATE TABLE {self._table_name} (
                    id char(36),
                    term TEXT,
                    timestamp BIGINT
                );""")

            self._cursor.execute(f"""
                CREATE INDEX index_timestamp
                ON {self._table_name} (timestamp);""")

            self._conn.commit()

    def append(self, search):
        """Add search to search history

        :param search: (counter.Search) the search object to be added
        """
        query_values = {
            "id": str(search.id),
            "term": search.term,
            "timestamp": search.timestamp
        }

        self._cursor.execute(f"""
            INSERT INTO {self._table_name}
            VALUES (:id, :term, :timestamp);""", query_values)

        self._conn.commit()

    def num_arbitrary_lookback(self, seconds):
        """Return the number of searches made in the past seconds

        :param seconds: (int) The number of seconds in the past
        :returns: (int) The number of searches
        """
        num_searches = self._get_num_searches()
        offset = self._get_offset(seconds, num_searches + 1)

        return num_searches - offset

    def _get_offset(self, seconds, default):
        """Get the offset index in the search history that matches seconds

        It returns an offset index in the search history that matches
        the first search in the interval [now - seconds, now], now
        is calculated by using time.time_ns().

        :param seconds: (int) The number of seconds in the past
        :param default: (int) The default value for offset if
            no rowid is found for it
        :returns: (int) The offset
        """
        now_nanosec = time.time_ns()
        target_nanosec = now_nanosec - utils.seconds_in_nano(seconds)

        query_values = {
            "target_nanosec": target_nanosec
        }

        self._cursor.execute(f"""
            SELECT rowid
            FROM {self._table_name}
            WHERE timestamp >= :target_nanosec
            ORDER BY timestamp
            LIMIT 1;""", query_values)

        offset_row = self._cursor.fetchone()
        rowid = offset_row[0] if offset_row else default

        return rowid - 1

    def _get_num_searches(self):
        """Get the number of searches in the search history"""
        self._cursor.execute(f"""
            SELECT COALESCE(MAX(rowid), 0)
            FROM {self._table_name};""", {"table": self._table_name})

        num_searches = self._cursor.fetchone()[0]
        return num_searches

    def most_common_term(self, seconds):
        """Return the most commonly searched term in the past seconds

        :param seconds: (int) The number of seconds in the past
        :returns: (int) The most commonly searched term
        """
        now_nanosec = time.time_ns()
        target_nanosec = now_nanosec - utils.seconds_in_nano(seconds)

        query_values = {
            "table": self._table_name,
            "target_nanosec": target_nanosec
        }

        self._cursor.execute(f"""
            SELECT term, COUNT(*) as occurs
            FROM {self._table_name}
            WHERE timestamp >= :target_nanosec
            GROUP BY term
            ORDER BY occurs DESC
            LIMIT 1;""", query_values)

        most_common_row = self._cursor.fetchone()
        if most_common_row:
            return most_common_row[0]
