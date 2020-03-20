class ElasticSearchException(Exception):
    pass


class SearchException(ElasticSearchException):
    pass


class UnexpectedResult(SearchException):
    pass
