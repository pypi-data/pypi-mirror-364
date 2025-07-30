import base64
import datetime
from http.cookiejar import CookieJar

from htls.cffi import GoException
from htls.client.utils import complexjson
from htls.cffi.objects import Response as TLSResponse
from htls.client import PreparedRequest, CaseInsensitiveDict, \
    extract_cookies_to_jar, codes, HTTPError, \
    chardet, guess_json_utf, get_encoding_from_headers


class Response:
    def __init__(self):
        self._content = None
        self.status_code = 0
        self.headers = CaseInsensitiveDict()
        self.url = None
        self.encoding = None
        self.history = []
        self.reason = None
        self.cookies = None
        self.elapsed = datetime.timedelta(0)
        self.request: PreparedRequest | None = None

        self.raw: TLSResponse | None = None
        self._exception = None

    def build_response(self, request: PreparedRequest, response: TLSResponse):
        self.request = request
        self.raw = response
        self._exception = response._exception

        if self._exception:
            return

        self.url = response.target
        self.status_code = response.status
        self.reason = codes.get(self.status_code, "Unknown Reason")
        headers = []
        for header_name, header_values in response.headers.items():
            headers.append((header_name, ", ".join(header_values)))
        self.headers = CaseInsensitiveDict(headers)
        self.encoding = get_encoding_from_headers(self.headers)

        self.cookies = CookieJar()
        extract_cookies_to_jar(self.cookies, request, response.headers)

        self._content = base64.b64decode(
            response.body.split(",")[1]) if response.body else None

    def __repr__(self):
        if self._exception:
            return f"<GoException: {self._exception.args}>"
        return f"<Response [{self.status_code}]>"

    def __bool__(self):
        return self.ok

    def raise_for_exception(self):
        if self._exception:
            raise self._exception

    def raise_for_status(self):
        http_error_msg = ""
        if 400 <= self.status_code < 500:
            http_error_msg = f"{self.status_code} Client Error: {self.reason} for url: {self.url}"
        elif 500 <= self.status_code < 600:
            http_error_msg = f"{self.status_code} Server Error: {self.reason} for url: {self.url}"
        if http_error_msg:
            raise HTTPError(http_error_msg)

    @property
    def ok(self):
        try:
            self.raise_for_exception()
            self.raise_for_status()
        except HTTPError:
            return False
        except GoException:
            return False
        return True

    @property
    def is_redirect(self):
        return "location" in self.headers and self.status_code in (
            301,  # moved
            302,  # found
            303,  # other
            307,  # temporary redirect
            308  # permanent redirect
        )

    @property
    def is_permanent_redirect(self):
        return "location" in self.headers and self.status_code in (
            301,  # moved permanently
            308  # permanent redirect
        )

    @property
    def apparent_encoding(self):
        """
        this method was copied from requests library
        """
        if chardet is not None:
            return chardet.detect(self.content)["encoding"]
        else:
            # If no character detection library is available, we'll fall back
            # to a standard Python utf-8 str.
            return "utf-8"

    @property
    def content(self):
        return self._content

    @property
    def text(self):
        encoding = self.encoding

        if not self.content:
            return ""

        if self.encoding is None:
            encoding = self.apparent_encoding

        try:
            content = str(self.content, encoding, errors="replace")
        except (LookupError, TypeError):
            content = str(self.content, errors="replace")

        return content

    def json(self, **kwargs):
        r"""
        this method was copied from requests library
        Decodes the JSON response body (if any) as a Python object.

        This may return a dictionary, list, etc. depending on what is in the response.

        :param \*\*kwargs: Optional arguments that ``json.loads`` takes.
        :raises requests.exceptions.JSONDecodeError: If the response body does not
            contain valid json.
        """

        if not self.encoding and self.content and len(self.content) > 3:
            # No encoding set. JSON RFC 4627 section 3 states we should expect
            # UTF-8, -16 or -32. Detect which one to use; If the detection or
            # decoding fails, fall back to `self.text` (using charset_normalizer to make
            # a best guess).
            encoding = guess_json_utf(self.content)
            if encoding is not None:
                try:
                    return complexjson.loads(self.content.decode(encoding),
                                             **kwargs)
                except UnicodeDecodeError:
                    # Wrong UTF codec detected; usually because it's not UTF-8
                    # but some other 8-bit codec.  This is an RFC violation,
                    # and the server didn't bother to tell us what codec *was*
                    # used.
                    pass

        return complexjson.loads(self.text, **kwargs)
