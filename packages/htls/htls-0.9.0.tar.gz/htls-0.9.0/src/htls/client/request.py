from typing import TYPE_CHECKING, Any, Callable, Sequence

if TYPE_CHECKING:
    from htls import AuthBase


class Request:
    def __init__(
            self,
            method: str,
            url: str,
            params: dict[str, str] = None,
            data: Any | None = None,
            headers: dict[str, str] = None,
            cookies: dict[str, str] = None,
            auth: "AuthBase" = None,
            timeout: float = None,
            allow_redirects: bool = True,
            proxies: dict[str, str] = None,
            hooks: dict[str, Callable | Sequence[Callable]] = None,
            verify: bool = False,
            json: dict | list | None = None,

            force_http1: bool = False,
            header_order: list[str] | None = None,
            request_host_override: str | None = None,
            server_name_overwrite: str | None = None,

            stream_output_block_size: int | None = None,
            stream_output_eof_symbol: str | None = None,
            stream_output_path: str | None = None,
    ):
        self.method = method
        self.url = url
        self.params = params
        self.data = data
        self.headers = headers
        self.cookies = cookies
        self.auth = auth
        self.timeout = timeout
        self.allow_redirects = allow_redirects
        self.proxies = proxies
        self.hooks = hooks
        self.verify = verify
        self.json = json

        self.force_http1 = force_http1
        self.header_order = header_order
        self.request_host_override = request_host_override
        self.server_name_overwrite = server_name_overwrite

        self.stream_output_block_size = stream_output_block_size
        self.stream_output_eof_symbol = stream_output_eof_symbol
        self.stream_output_path = stream_output_path
