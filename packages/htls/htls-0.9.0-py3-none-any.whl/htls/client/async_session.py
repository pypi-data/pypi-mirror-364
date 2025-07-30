import time
import base64
from datetime import timedelta
from asyncio import Lock
from typing import Any, Callable
from urllib.parse import urlparse, urljoin

from htls.client import Session
from htls.cffi import CustomTLSClient, async_destroy_session
from htls.client.request import Request
from htls.cffi.funcs import request as do_tls_request
from htls.client.prepared_request import PreparedRequest
from htls.cffi.objects.request import TransportOptions, Request as TLSRequest
from htls.client import Response, extract_cookies_to_jar, TooManyRedirects, \
    requote_uri, merge_cookies, \
    AuthBase, dispatch_hook


class AsyncSession(Session):
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
        super().__init__(tls_client_identifier, custom_tls_client, catch_panics,
                         certificate_pinning_hosts,
                         transport_options, default_headers, connect_headers,
                         disable_ipv6, disable_ipv4, local_address,
                         session_id, with_debug, with_default_cookie_jar,
                         without_cookie_jar,
                         with_random_tls_extension_order, max_redirects)
        self._lock = Lock()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclose()

    async def aclose(self):
        if self._memory_allocated:
            await async_destroy_session(self.session_id)
            self._memory_allocated = False

    async def resolve_redirects(
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
                resp = await self.send(
                    req
                )

                extract_cookies_to_jar(self.cookies, prepared_request,
                                       resp.raw.headers)

                # extract redirect url, if any, for the next loop
                url = self.get_redirect_target(resp)
                yield resp

    async def send(self, prep: PreparedRequest) -> Response:
        async with self._lock:
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
                "headers": prep.headers,
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
            history = [resp async for resp in gen]
        else:
            history = []

        if history:
            history.insert(0, rsp)
            rsp = history.pop()
            rsp.history = history

        return rsp

    async def request(
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
                          timeout, allow_redirects, hooks, proxies,
                          verify, json, force_http1, header_order,
                          request_host_override, server_name_overwrite,
                          stream_output_block_size, stream_output_eof_symbol,
                          stream_output_path)
        if return_request:
            return request

        prep = self.prepare_request(request)
        rsp = await self.send(prep)

        return rsp

    async def get(
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
        return await self.request(
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

    async def options(
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
        return await self.request(
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

    async def head(
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
        return await self.request(
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

    async def post(
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
        return await self.request(
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

    async def put(
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
        return await self.request(
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

    async def patch(
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
        return await self.request(
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

    async def delete(
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
        return await self.request(
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
