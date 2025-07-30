from htls import TLSClientException


class InvalidURL(TLSClientException, ValueError):
    pass


class MissingSchema(TLSClientException, ValueError):
    pass


class InvalidJSONError(TLSClientException, ValueError):
    pass


class HTTPError(TLSClientException):
    pass


class TooManyRedirects(TLSClientException):
    pass
