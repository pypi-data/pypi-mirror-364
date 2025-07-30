import time
import uuid
import base64
from datetime import timedelta
from threading import Lock
from typing import Any, Callable
from http.cookiejar import CookieJar
from urllib.parse import urlparse, urljoin

from htls.cffi import CustomTLSClient, destroy_session
from htls.client.request import Request
from htls.cffi.funcs import request as do_tls_request
from htls.client.prepared_request import PreparedRequest
from htls.cffi.objects.request import TransportOptions, Request as TLSRequest
from htls.client import Response, extract_cookies_to_jar, TooManyRedirects, \
    requote_uri, merge_cookies, \
    AuthBase, dispatch_hook


class Session:
    def __init__(
            self,
            tls_client_identifier: str = "",
            custom_tls_client: CustomTLSClient | dict | None = None,

            catch_panics: bool = False,
            certificate_pinning_hosts: dict | None = None,
            transport_options: TransportOptions | dict | None = None,
            default_headers: dict[str, list[str]] | None = None,
            connect_headers: dict[str, list[str]] | None = None,
            disable_ipv6: bool = False,
            disable_ipv4: bool = False,
            local_address: str | None = None,
            session_id: str | None = None,
            with_debug: bool = False,
            with_default_cookie_jar: bool = False,
            without_cookie_jar: bool = False,
            with_random_tls_extension_order: bool = False,

            max_redirects: int = 30
    ):
        self.catch_panics = catch_panics
        self.certificate_pinning_hosts = certificate_pinning_hosts
        self.custom_tls_client = custom_tls_client
        self.transport_options = transport_options
        self.default_headers = default_headers
        self.connect_headers = connect_headers
        self.disable_ipv6 = disable_ipv6
        self.disable_ipv4 = disable_ipv4
        self.local_address = local_address
        self.session_id = str(session_id) or str(uuid.uuid4())
        self.tls_client_identifier = tls_client_identifier
        self.with_debug = with_debug
        self.with_default_cookie_jar = with_default_cookie_jar
        self.without_cookie_jar = without_cookie_jar
        self.with_random_tls_extension_order = with_random_tls_extension_order

        self.cookies = CookieJar()
        self.max_redirects = max_redirects
        self._memory_allocated = False
        self._lock = Lock()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.close()

    def __del__(self):
        self.close()

    def close(self):
        if self._memory_allocated:
            destroy_session(self.session_id)
            self._memory_allocated = False

    def rebuild_method(self, prepared_request, response):
        """
        this method was copied from requests library
        When being redirected we may want to change the method of the request
        based on certain specs or browser behavior.
        """
        method = prepared_request.method

        # https://tools.ietf.org/html/rfc7231#section-6.4.4
        if response.status_code == 303 and method != "HEAD":
            method = "GET"

        # Do what the browsers do, despite standards...
        # First, turn 302s into GETs.
        if response.status_code == 302 and method != "HEAD":
            method = "GET"

        # Second, if a POST is responded to with a 301, turn it into a GET.
        # This bizarre behaviour is explained in Issue 1704.
        if response.status_code == 301 and method == "POST":
            method = "GET"

        prepared_request.method = method

    def get_redirect_target(self, resp: Response):
        """
        this method was copied from requests library
        Receives a Response. Returns a redirect URI or ``None``
        """
        # Due to the nature of how requests processes redirects this method will
        # be called at least once upon the original response and at least twice
        # on each subsequent redirect response (if any).
        # If a custom mixin is used to handle this logic, it may be advantageous
        # to cache the redirect location onto the response object as a private
        # attribute.
        if resp.is_redirect:
            location = resp.headers["location"]
            # Currently the underlying http module on py3 decode headers
            # in latin1, but empirical evidence suggests that latin1 is very
            # rarely used with non-ASCII characters in HTTP headers.
            # It is more likely to get UTF8 header rather than latin1.
            # This causes incorrect handling of UTF8 encoded location headers.
            # To solve this, we re-encode the location in latin1.
            location = location.encode("latin1")
            return str(location, "utf8")
        return None

    def resolve_redirects(
            self,
            resp: Response,
            req: PreparedRequest,
            yield_requests: bool = False
    ):
        """
        this method was partially copied from requests library
        Receives a Response. Returns a generator of Responses or Requests.
        """
        history = []  # keep track of history

        url = self.get_redirect_target(resp)
        previous_fragment = urlparse(req.url).fragment
        while url:
            prepared_request = req.copy()

            # Update history and keep track of redirects.
            # resp.history must ignore the original request in this loop
            history.append(resp)
            resp.history = history[1:]
            if resp._exception:
                return

            if len(resp.history) >= self.max_redirects:
                raise TooManyRedirects(
                    f"Exceeded {self.max_redirects} redirects."
                )

            # Handle redirection without scheme (see: RFC 1808 Section 4)
            if url.startswith("//"):
                parsed_rurl = urlparse(resp.url)
                url = ":".join([str(parsed_rurl.scheme), url])

            # Normalize url case and attach previous fragment if needed (RFC 7231 7.1.2)
            parsed = urlparse(url)
            if parsed.fragment == "" and previous_fragment:
                parsed = parsed._replace(fragment=previous_fragment)
            elif parsed.fragment:
                previous_fragment = parsed.fragment
            url = parsed.geturl()

            # Facilitate relative 'location' headers, as allowed by RFC 7231.
            # (e.g. '/path/to/resource' instead of 'http://domain.tld/path/to/resource')
            # Compliant with RFC3986, we percent encode the url.
            if not parsed.netloc:
                url = urljoin(resp.url, requote_uri(url))
            else:
                url = requote_uri(url)

            prepared_request.url = str(url)

            self.rebuild_method(prepared_request, resp)

            # https://github.com/psf/requests/issues/1084
            if resp.status_code not in (
                    307,  # temporary redirect,
                    308  # permanent redirect,
            ):
                # https://github.com/psf/requests/issues/3490
                purged_headers = (
                "Content-Length", "Content-Type", "Transfer-Encoding")
                for header in purged_headers:
                    prepared_request.headers.pop(header, None)
                prepared_request.body = None

            headers = prepared_request.headers
            headers.pop("Cookie", None)

            # Extract any cookies sent on the response to the cookiejar
            # in the new request. Because we've mutated our copied prepared
            # request, use the old one that we haven't yet touched.
            extract_cookies_to_jar(prepared_request._cookies, req,
                                   resp.raw.headers)
            merge_cookies(prepared_request._cookies, self.cookies)
            prepared_request.prepare_cookies(prepared_request._cookies)

            # TODO Rebuild auth and proxy information.
            # proxies = self.rebuild_proxies(prepared_request, proxies)
            # self.rebuild_auth(prepared_request, resp)

            # Override the original request.
            req = prepared_request

            if yield_requests:
                yield req
            else:
                resp = self.send(
                    req
                )

                extract_cookies_to_jar(self.cookies, prepared_request,
                                       resp.raw.headers)

                # extract redirect url, if any, for the next loop
                url = self.get_redirect_target(resp)
                yield resp

    def send(self, prep: PreparedRequest) -> Response:
        with self._lock:
            self._memory_allocated = True
            prep = dispatch_hook("request", prep.hooks, prep)

            params = {}
            session_params = dict(self.__dict__)
            session_params.pop("cookies", None)
            session_params.pop("max_redirects", None)
            session_params.pop("_memory_allocated", None)
            session_params.pop("_lock", None)
            params.update(session_params)
            params.update(prep.tls_params)
            params.update({
                "headers": dict(prep.headers.items()),
                "request_body": base64.b64encode(prep.body).decode(
                    "utf-8") if prep.body else None,
                "request_method": prep.method,
                "request_url": prep.url
            })

            tls_request = TLSRequest(**params)

            start = time.time()
            tls_response = do_tls_request(tls_request)
            elapsed = time.time() - start

            rsp = Response()
            rsp.build_response(prep, tls_response)
            rsp.elapsed = timedelta(seconds=elapsed)

        if rsp._exception:
            return rsp

        rsp = dispatch_hook("response", prep.hooks, rsp)

        if rsp.history:
            resp: Response
            for resp in rsp.history:
                extract_cookies_to_jar(self.cookies, resp.request, resp.headers)

        extract_cookies_to_jar(self.cookies, rsp.request, rsp.headers)

        if prep.raw.allow_redirects:
            gen = self.resolve_redirects(rsp, prep)
            history = [resp for resp in gen]
        else:
            history = []

        if history:
            history.insert(0, rsp)
            rsp = history.pop()
            rsp.history = history

        return rsp

    def prepare_request(self, request: Request) -> PreparedRequest:
        original_cookies = request.cookies
        merged_cookies = merge_cookies(
            merge_cookies(CookieJar(), self.cookies), original_cookies
        )
        request.cookies = merged_cookies
        prep = PreparedRequest()
        prep.prepare_request(request)
        request.cookies = original_cookies
        return prep

    def request(
            self,
            method: str,
            url: str,
            params: dict[str, str] = None,
            data: Any | None = None,
            headers: dict[str, str] = None,
            cookies: dict[str, str] = None,
            auth: AuthBase = None,
            timeout: float = None,
            allow_redirects: bool = True,
            proxies: dict[str, str] = None,
            hooks: dict[str, Callable] = None,
            verify: bool = False,
            json: dict | list | None = None,

            force_http1: bool = False,
            header_order: list[str] | None = None,
            request_host_override: str | None = None,
            server_name_overwrite: str | None = None,

            stream_output_block_size: int | None = None,
            stream_output_eof_symbol: str | None = None,
            stream_output_path: str | None = None,

            return_request: bool = False
    ):
        request = Request(method, url, params, data, headers, cookies, auth,
                          timeout, allow_redirects, proxies, hooks,
                          verify, json, force_http1, header_order,
                          request_host_override, server_name_overwrite,
                          stream_output_block_size, stream_output_eof_symbol,
                          stream_output_path)
        if return_request:
            return request

        prep = self.prepare_request(request)
        rsp = self.send(prep)

        return rsp

    def get(
            self,
            url: str,
            params: dict[str, str] = None,
            headers: dict[str, str] = None,
            cookies: dict[str, str] = None,
            auth: AuthBase = None,
            timeout: float = None,
            allow_redirects: bool = True,
            proxies: dict[str, str] = None,
            hooks: dict[str, Callable] = None,
            verify: bool = False,

            force_http1: bool = False,
            header_order: list[str] | None = None,
            request_host_override: str | None = None,
            server_name_overwrite: str | None = None,

            stream_output_block_size: int | None = None,
            stream_output_eof_symbol: str | None = None,
            stream_output_path: str | None = None,

            return_request: bool = False
    ):
        return self.request(
            method="GET",
            url=url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            allow_redirects=allow_redirects,
            proxies=proxies,
            hooks=hooks,
            verify=verify,
            force_http1=force_http1,
            header_order=header_order,
            request_host_override=request_host_override,
            server_name_overwrite=server_name_overwrite,
            stream_output_block_size=stream_output_block_size,
            stream_output_eof_symbol=stream_output_eof_symbol,
            stream_output_path=stream_output_path,
            return_request=return_request
        )

    def options(
            self,
            url: str,
            params: dict[str, str] = None,
            data: Any | None = None,
            headers: dict[str, str] = None,
            cookies: dict[str, str] = None,
            auth: AuthBase = None,
            timeout: float = None,
            allow_redirects: bool = True,
            proxies: dict[str, str] = None,
            hooks: dict[str, Callable] = None,
            verify: bool = False,
            json: dict | list | None = None,

            force_http1: bool = False,
            header_order: list[str] | None = None,
            request_host_override: str | None = None,
            server_name_overwrite: str | None = None,

            stream_output_block_size: int | None = None,
            stream_output_eof_symbol: str | None = None,
            stream_output_path: str | None = None,

            return_request: bool = False
    ):
        return self.request(
            method="OPTIONS",
            url=url,
            params=params,
            data=data,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            allow_redirects=allow_redirects,
            proxies=proxies,
            hooks=hooks,
            verify=verify,
            json=json,
            force_http1=force_http1,
            header_order=header_order,
            request_host_override=request_host_override,
            server_name_overwrite=server_name_overwrite,
            stream_output_block_size=stream_output_block_size,
            stream_output_eof_symbol=stream_output_eof_symbol,
            stream_output_path=stream_output_path,
            return_request=return_request
        )

    def head(
            self,
            url: str,
            params: dict[str, str] = None,
            headers: dict[str, str] = None,
            cookies: dict[str, str] = None,
            auth: AuthBase = None,
            timeout: float = None,
            allow_redirects: bool = True,
            proxies: dict[str, str] = None,
            hooks: dict[str, Callable] = None,
            verify: bool = False,

            force_http1: bool = False,
            header_order: list[str] | None = None,
            request_host_override: str | None = None,
            server_name_overwrite: str | None = None,

            stream_output_block_size: int | None = None,
            stream_output_eof_symbol: str | None = None,
            stream_output_path: str | None = None,

            return_request: bool = False
    ):
        return self.request(
            method="HEAD",
            url=url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            allow_redirects=allow_redirects,
            proxies=proxies,
            hooks=hooks,
            verify=verify,
            force_http1=force_http1,
            header_order=header_order,
            request_host_override=request_host_override,
            server_name_overwrite=server_name_overwrite,
            stream_output_block_size=stream_output_block_size,
            stream_output_eof_symbol=stream_output_eof_symbol,
            stream_output_path=stream_output_path,
            return_request=return_request
        )

    def post(
            self,
            url: str,
            params: dict[str, str] = None,
            data: Any | None = None,
            headers: dict[str, str] = None,
            cookies: dict[str, str] = None,
            auth: AuthBase = None,
            timeout: float = None,
            allow_redirects: bool = True,
            proxies: dict[str, str] = None,
            hooks: dict[str, Callable] = None,
            verify: bool = False,
            json: dict | list | None = None,

            force_http1: bool = False,
            header_order: list[str] | None = None,
            request_host_override: str | None = None,
            server_name_overwrite: str | None = None,

            stream_output_block_size: int | None = None,
            stream_output_eof_symbol: str | None = None,
            stream_output_path: str | None = None,

            return_request: bool = False
    ):
        return self.request(
            method="POST",
            url=url,
            params=params,
            data=data,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            allow_redirects=allow_redirects,
            proxies=proxies,
            hooks=hooks,
            verify=verify,
            json=json,
            force_http1=force_http1,
            header_order=header_order,
            request_host_override=request_host_override,
            server_name_overwrite=server_name_overwrite,
            stream_output_block_size=stream_output_block_size,
            stream_output_eof_symbol=stream_output_eof_symbol,
            stream_output_path=stream_output_path,
            return_request=return_request
        )

    def put(
            self,
            url: str,
            params: dict[str, str] = None,
            data: Any | None = None,
            headers: dict[str, str] = None,
            cookies: dict[str, str] = None,
            auth: AuthBase = None,
            timeout: float = None,
            allow_redirects: bool = True,
            proxies: dict[str, str] = None,
            hooks: dict[str, Callable] = None,
            verify: bool = False,
            json: dict | list | None = None,

            force_http1: bool = False,
            header_order: list[str] | None = None,
            request_host_override: str | None = None,
            server_name_overwrite: str | None = None,

            stream_output_block_size: int | None = None,
            stream_output_eof_symbol: str | None = None,
            stream_output_path: str | None = None,

            return_request: bool = False
    ):
        return self.request(
            method="PUT",
            url=url,
            params=params,
            data=data,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            allow_redirects=allow_redirects,
            proxies=proxies,
            hooks=hooks,
            verify=verify,
            json=json,
            force_http1=force_http1,
            header_order=header_order,
            request_host_override=request_host_override,
            server_name_overwrite=server_name_overwrite,
            stream_output_block_size=stream_output_block_size,
            stream_output_eof_symbol=stream_output_eof_symbol,
            stream_output_path=stream_output_path,
            return_request=return_request
        )

    def patch(
            self,
            url: str,
            params: dict[str, str] = None,
            data: Any | None = None,
            headers: dict[str, str] = None,
            cookies: dict[str, str] = None,
            auth: AuthBase = None,
            timeout: float = None,
            allow_redirects: bool = True,
            proxies: dict[str, str] = None,
            hooks: dict[str, Callable] = None,
            verify: bool = False,
            json: dict | list | None = None,

            force_http1: bool = False,
            header_order: list[str] | None = None,
            request_host_override: str | None = None,
            server_name_overwrite: str | None = None,

            stream_output_block_size: int | None = None,
            stream_output_eof_symbol: str | None = None,
            stream_output_path: str | None = None,

            return_request: bool = False
    ):
        return self.request(
            method="PATCh",
            url=url,
            params=params,
            data=data,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            allow_redirects=allow_redirects,
            proxies=proxies,
            hooks=hooks,
            verify=verify,
            json=json,
            force_http1=force_http1,
            header_order=header_order,
            request_host_override=request_host_override,
            server_name_overwrite=server_name_overwrite,
            stream_output_block_size=stream_output_block_size,
            stream_output_eof_symbol=stream_output_eof_symbol,
            stream_output_path=stream_output_path,
            return_request=return_request
        )

    def delete(
            self,
            url: str,
            params: dict[str, str] = None,
            data: Any | None = None,
            headers: dict[str, str] = None,
            cookies: dict[str, str] = None,
            auth: AuthBase = None,
            timeout: float = None,
            allow_redirects: bool = True,
            proxies: dict[str, str] = None,
            hooks: dict[str, Callable] = None,
            verify: bool = False,
            json: dict | list | None = None,

            force_http1: bool = False,
            header_order: list[str] | None = None,
            request_host_override: str | None = None,
            server_name_overwrite: str | None = None,

            stream_output_block_size: int | None = None,
            stream_output_eof_symbol: str | None = None,
            stream_output_path: str | None = None,

            return_request: bool = False
    ):
        return self.request(
            method="DELETE",
            url=url,
            params=params,
            data=data,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            allow_redirects=allow_redirects,
            proxies=proxies,
            hooks=hooks,
            verify=verify,
            json=json,
            force_http1=force_http1,
            header_order=header_order,
            request_host_override=request_host_override,
            server_name_overwrite=server_name_overwrite,
            stream_output_block_size=stream_output_block_size,
            stream_output_eof_symbol=stream_output_eof_symbol,
            stream_output_path=stream_output_path,
            return_request=return_request
        )
