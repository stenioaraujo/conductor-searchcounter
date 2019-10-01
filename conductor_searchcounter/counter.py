import random
import time
import uuid

from conductor_searchcounter import dao


class Search:
    def __init__(self, search_id, search_term, search_timestamp):
        """Create an instance of Search

        :param search_id: (UUID) A unique identifier.
        :param search_term: (str) The search term.
        :param search_timestamp: (int) The nanoseconds since the epoch.
        """
        self._id = search_id
        self._term = search_term
        self._timestamp = search_timestamp

    @property
    def id(self):
        return self._id

    @property
    def term(self):
        return self._term

    @property
    def timestamp(self):
        return self._timestamp

    def __lt__(self, other):
        return self.timestamp < other.timestamp


class SearchCounter:
    def __init__(self, search_terms, dao_instance=None):
        """Create an instance of SearchCounter

        :param search_terms: ([str]) The list of search terms to be used
        :param dao_instance: (dao.DAO) An instance of any subclass of DAO.
            If dao is None, dao will be an instance of dao.DAOList
        """
        self._search_terms = list(search_terms)
        self._dao = dao_instance

        if self._dao is None:
            self._dao = dao.DAOList()

    def increment(self):
        """Add a search to the collection

        The search term is assigned randomly from the the list of
        search terms passed to the SearchCounter constructor
        """
        search_id = uuid.uuid4()
        search_term = random.choice(self._search_terms)
        search_timestamp = time.time_ns()

        search = Search(search_id, search_term, search_timestamp)

        self._dao.append(search)

    def num_last_minute(self):
        """Return the number of searches made in the past minute

        :returns: (int) The number of searches
        """
        return self.num_arbitrary_lookback(60)

    def num_arbitrary_lookback(self, seconds):
        """Return the number of searches made in the past seconds

        :param seconds: (int) The number of seconds in the past
        :returns: (int) The number of searches
        """
        return self._dao.num_arbitrary_lookback(seconds)

    def most_common_term(self, seconds):
        """Return the most commonly searched term in the past seconds

        :param seconds: (int) The number of seconds in the past
        :returns: (int) The most commonly searched term
        """
        return self._dao.most_common_term(seconds)
