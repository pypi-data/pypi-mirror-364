from copy import deepcopy
from http.cookiejar import CookieJar, Cookie
from typing import Mapping, Callable, Sequence
from urllib.parse import urlparse, urlencode, urlunparse

import idna

from htls.client.request import Request
from htls.client.utils import _copy_cookie_jar, complexjson
from htls.client.exceptions import MissingSchema, InvalidURL, InvalidJSONError
from htls.client import CaseInsensitiveDict, requote_uri, cookiejar_from_dict, \
    AuthBase, default_hooks


class PreparedRequest:
    def __init__(self):
        self.method = None
        self.url = None
        self.headers = None
        self.body = None
        self.tls_params = {}
        self.raw: Request | None = None
        self.auth: AuthBase | None = None
        self.hooks: dict[str, list[Callable]] | None = default_hooks()

        self._cookies: CookieJar | None = None
        self._scheme: str | None = None

    def __repr__(self):
        return f"<PreparedRequest [{self.method}]>"

    def copy(self):
        p = PreparedRequest()
        p.method = self.method
        p.url = self.url
        p.headers = self.headers.copy() if self.headers is not None else CaseInsensitiveDict()
        p._cookies = _copy_cookie_jar(self._cookies)
        p._scheme = self._scheme
        p.body = self.body
        p.raw = self.raw
        p.auth = self.auth
        p.hooks = deepcopy(
            self.hooks) if self.hooks is not None else default_hooks()
        p.tls_params = self.tls_params.copy() if self.tls_params is not None else {}
        return p

    @staticmethod
    def _encode_params(data):
        # this method was copied from requests library
        if isinstance(data, (str, bytes)):
            return data
        elif hasattr(data, "read"):
            # change because this library don't support readable body
            return data.read()
        elif hasattr(data, "__iter__"):
            result = []
            if isinstance(data, Mapping):
                data = list(data.items())
            for k, vs in data:
                if isinstance(vs, (str, bytes)) or not hasattr(vs, "__iter__"):
                    vs = [vs]
                for v in vs:
                    if v is not None:
                        result.append(
                            (
                                k.encode("utf-8") if isinstance(k, str) else k,
                                v.encode("utf-8") if isinstance(v, str) else v,
                            )
                        )
            return urlencode(result, doseq=True)
        else:
            return data

    def prepare_request(self, request: Request):
        self.raw = request

        self.prepare_method(request.method)
        self.prepare_url(request.url, request.params)
        self.prepare_headers(request.headers)
        self.prepare_cookies(request.cookies)
        self.prepare_body(request.data, request.json)
        self.prepare_tls_params(request)
        self.prepare_auth(request.auth)

        self.prepare_hooks(request.hooks)
        self.prepare_proxies(request.proxies)

    def prepare_method(self, method):
        # this method was partially copied from requests library
        if isinstance(method, bytes):
            self.method = method.decode("utf8")
        else:
            self.method = str(method)
        self.method.upper()

    def prepare_url(self, url, params):
        # this method was partially copied from requests library
        if isinstance(url, bytes):
            url = url.decode("utf8")
        else:
            url = str(url)
        url = url.lstrip()

        if ":" in url and not url.lower().startswith("http"):
            self.url = url
            return

        result = urlparse(url)
        scheme, auth, host, port, path, query, fragment = (
            result.scheme,
            f"{result.username}{':' + result.password if result.password else ''}" if result.username else None,
            result.hostname,
            result.port,
            result.path,
            result.query,
            result.fragment,
        )
        if not scheme:
            raise MissingSchema(
                f"Invalid URL {url!r}: No scheme supplied. "
                f"Perhaps you meant https://{url}?"
            )
        self._scheme = scheme

        if not host:
            raise InvalidURL(f"Invalid URL {url!r}: No host supplied")

        is_ascii = True
        try:
            host.encode('ascii')
        except UnicodeEncodeError:
            is_ascii = False

        if not is_ascii:
            try:
                host = idna.encode(host, uts46=True).decode('utf-8')
            except idna.IDNAError:
                raise InvalidURL("URL has an invalid label.")
        elif host.startswith(("*", ".")):
            raise InvalidURL("URL has an invalid label.")

        netloc = auth or ""
        if netloc:
            netloc += "@"
        netloc += host
        if port:
            netloc += f":{port}"

        if not path:
            path = "/"

        if isinstance(params, (str, bytes)):
            if isinstance(params, bytes):
                params = params.decode("ascii")

        enc_params = self._encode_params(params)
        if enc_params:
            if query:
                query = f"{query}&{enc_params}"
            else:
                query = enc_params

        uri = urlunparse([scheme, netloc, path, None, query, fragment])
        self.url = requote_uri(uri)

    def prepare_headers(self, headers):
        """
        # this method was partially copied from requests library
        Prepares the given HTTP headers.
        """

        self.headers = CaseInsensitiveDict()
        if headers:
            for header in headers.items():
                # Raise exception on invalid header value.
                name, value = header
                self.headers[str(name)] = value

    def prepare_cookies(self, cookies):
        # this method was partially copied from requests library
        cookies = cookies or {}

        if isinstance(cookies, CookieJar):
            self._cookies = cookies
        else:
            self._cookies = cookiejar_from_dict(cookies)

        cookie: Cookie
        cookies = [{
            "domain": cookie.domain,
            "expires": int(cookie.expires or 0),
            "maxAge": 0,
            "name": cookie.name,
            "path": cookie.path,
            "value": cookie.value
        } for cookie in self._cookies]

        self.tls_params["request_cookies"] = cookies

    def prepare_body(self, data, json):
        # this method was partially copied from requests library
        body = None
        content_type = None

        if not data and json is not None:
            content_type = "application/json"

            try:
                body = complexjson.dumps(json, allow_nan=False)
            except ValueError as ve:
                raise InvalidJSONError(ve)

            if not isinstance(body, bytes):
                body = body.encode("utf-8")

        if data:
            body = self._encode_params(data)
            if isinstance(data, (str, bytes)):
                content_type = None
            else:
                content_type = "application/x-www-form-urlencoded"

        self.prepare_content_length(body)
        if content_type and ("content-type" not in self.headers):
            self.headers["Content-Type"] = content_type

        self.body = body

    def prepare_content_length(self, body):
        # this method was partially copied from requests library
        if body is not None:
            length = len(body)
            if length:
                self.headers["Content-Length"] = str(length)
        elif (
                self.method not in ("GET", "HEAD")
                and self.headers.get("Content-Length") is None
        ):
            self.headers["Content-Length"] = "0"

    def prepare_tls_params(self, request: Request):
        self.tls_params.update({
            "follow_redirects": False,
            "force_http1": request.force_http1,
            "header_order": request.header_order,
            "insecure_skip_verify": request.verify,
            "is_byte_request": True,
            "is_byte_response": True,
            "is_rotating_proxy": False,
            "request_host_override": request.request_host_override,
            "server_name_overwrite": request.server_name_overwrite,
            "stream_output_block_size": request.stream_output_block_size,
            "stream_output_eof_symbol": request.stream_output_eof_symbol,
            "stream_output_path": request.stream_output_path,
            "timeout_milliseconds": 0,
            "timeout_seconds": request.timeout
        })

    def prepare_auth(self, auth: AuthBase):
        """
        this method was partially copied from requests library
        Prepares the given HTTP auth data.
        """

        if auth:
            # Allow auth to make its changes.
            r = auth(self)

            # Update self to reflect the auth changes.
            self.__dict__.update(r.__dict__)

            # Recompute Content-Length
            self.prepare_content_length(self.body)

    def prepare_proxies(self, proxies: dict[str, str] | None):
        proxies = proxies or {}
        self.tls_params["proxy_url"] = proxies.get(self._scheme, None)

    def prepare_hooks(self, hooks: dict[str, Callable | Sequence[Callable]]):
        """
        this method was partially copied from requests library
        Prepares the given hooks.
        """
        # hooks can be passed as None to the prepare method and to this
        # method. To prevent iterating over None, simply use an empty list
        # if hooks is False-y
        hooks = hooks or []
        for event in hooks:
            self.register_hook(event, hooks[event])

    def register_hook(self, event: str, hook: Callable | Sequence[Callable]):
        """
        this method was copied from requests library
        Properly register a hook.
        """

        if event not in self.hooks:
            raise ValueError(
                f'Unsupported event specified, with event name "{event}"')

        if isinstance(hook, Callable):
            self.hooks[event].append(hook)
        elif hasattr(hook, "__iter__"):
            self.hooks[event].extend(h for h in hook if isinstance(h, Callable))
