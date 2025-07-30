from __future__ import annotations

from . import CustomTLSClient
from ..enums import *

"""
{
  "catchPanics": false,
  "certificatePinningHosts": null,
  "customTlsClient": null,
  "transportOptions": null,
  "followRedirects": false,
  "forceHttp1": false,
  "headerOrder": null,
  "headers": null,
  "insecureSkipVerify": false,
  "isByteRequest": false,
  "isByteResponse": false,
  "isRotatingProxy": false,
  "proxyUrl": null,
  "requestBody": null,
  "requestCookies": null,
  "requestHostOverride": null,
  "defaultHeaders": null,
  "connectHeaders": null,
  "requestMethod": "",
  "requestUrl": "",
  "disableIPV6": false,
  "disableIPV4": false,
  "localAddress": null,
  "sessionId": null,
  "serverNameOverwrite": "";
  "streamOutputBlockSize": null,
  "streamOutputEOFSymbol": null,
  "streamOutputPath": null,
  "timeoutMilliseconds": 0,
  "timeoutSeconds": 0,
  "tlsClientIdentifier": "",
  "withDebug": false,
  "withDefaultCookieJar": false,
  "withoutCookieJar": false,
  "withRandomTLSExtensionOrder": false
}
"""


class Request:
    def __init__(
            self,
            catch_panics: bool = False,
            certificate_pinning_hosts: dict | None = None,
            custom_tls_client: CustomTLSClient | dict | None = None,
            transport_options: TransportOptions | dict | None = None,
            follow_redirects: bool = False,
            force_http1: bool = False,
            header_order: list[str] | None = None,
            headers: dict[str, str] | None = None,
            insecure_skip_verify: bool = False,
            is_byte_request: bool = False,
            is_byte_response: bool = False,
            is_rotating_proxy: bool = False,
            proxy_url: str | None = None,
            request_body: str | bytes | None = None,
            request_cookies: list[dict] | None = None,
            request_host_override: str | None = None,
            default_headers: dict[str, list[str]] | None = None,
            connect_headers: dict[str, list[str]] | None = None,
            request_method: str = "",
            request_url: str = "",
            disable_ipv6: bool = False,
            disable_ipv4: bool = False,
            local_address: str | None = None,
            session_id: str | None = None,
            server_name_overwrite: str | None = None,
            stream_output_block_size: int | None = None,
            stream_output_eof_symbol: str | None = None,
            stream_output_path: str | None = None,
            timeout_milliseconds: int = 0,
            timeout_seconds: int = 0,
            tls_client_identifier: ClientIdentifier | str = "",
            with_debug: bool = False,
            with_default_cookie_jar: bool = False,
            without_cookie_jar: bool = False,
            with_random_tls_extension_order: bool = False
    ):
        self.catch_panics = catch_panics
        self.certificate_pinning_hosts = certificate_pinning_hosts
        self.custom_tls_client = custom_tls_client
        self.transport_options = transport_options
        self.follow_redirects = follow_redirects
        self.force_http1 = force_http1
        self.header_order = header_order
        self.headers = headers
        self.insecure_skip_verify = insecure_skip_verify
        self.is_byte_request = is_byte_request
        self.is_byte_response = is_byte_response
        self.is_rotating_proxy = is_rotating_proxy
        self.proxy_url = proxy_url
        self.request_body = request_body
        self.request_cookies = request_cookies
        self.request_host_override = request_host_override
        self.default_headers = default_headers
        self.connect_headers = connect_headers
        self.request_method = request_method
        self.request_url = request_url
        self.disable_ipv6 = disable_ipv6
        self.disable_ipv4 = disable_ipv4
        self.local_address = local_address
        self.session_id = session_id
        self.server_name_overwrite = server_name_overwrite
        self.stream_output_block_size = stream_output_block_size
        self.stream_output_eof_symbol = stream_output_eof_symbol
        self.stream_output_path = stream_output_path
        self.timeout_milliseconds = timeout_milliseconds
        self.timeout_seconds = timeout_seconds
        self.tls_client_identifier = tls_client_identifier
        self.with_debug = with_debug
        self.with_default_cookie_jar = with_default_cookie_jar
        self.without_cookie_jar = without_cookie_jar
        self.with_random_tls_extension_order = with_random_tls_extension_order

    def to_payload(self):
        return {
            "catchPanics": self.catch_panics,
            "certificatePinningHosts": self.certificate_pinning_hosts,
            "customTlsClient": (
                self.custom_tls_client.to_payload()
                if self.custom_tls_client is not None and
                   isinstance(self.custom_tls_client, CustomTLSClient)
                else self.custom_tls_client
            ),
            "transportOptions": (
                self.transport_options.to_payload()
                if self.transport_options is not None and
                   isinstance(self.transport_options, TransportOptions)
                else None
            ),
            "followRedirects": self.follow_redirects,
            "forceHttp1": self.force_http1,
            "headerOrder": self.header_order,
            "headers": dict(self.headers.items()),
            "insecureSkipVerify": self.insecure_skip_verify,
            "isByteRequest": self.is_byte_request,
            "isByteResponse": self.is_byte_response,
            "isRotatingProxy": self.is_rotating_proxy,
            "proxyUrl": self.proxy_url,
            "requestBody": self.request_body,
            "requestCookies": self.request_cookies,
            "requestHostOverride": self.request_host_override,
            "defaultHeaders": self.default_headers,
            "connectHeaders": self.connect_headers,
            "requestMethod": self.request_method,
            "requestUrl": self.request_url,
            "disableIPV6": self.disable_ipv6,
            "disableIPV4": self.disable_ipv4,
            "localAddress": self.local_address,
            "sessionId": self.session_id,
            "serverNameOverwrite": self.server_name_overwrite,
            "streamOutputBlockSize": self.stream_output_block_size,
            "streamOutputEOFSymbol": self.stream_output_eof_symbol,
            "streamOutputPath": self.stream_output_path,
            "timeoutMilliseconds": self.timeout_milliseconds,
            "timeoutSeconds": self.timeout_seconds,
            "tlsClientIdentifier": (
                self.tls_client_identifier
                if self.tls_client_identifier or self.custom_tls_client
                else ClientIdentifier.chrome_120
            ),
            "withDebug": self.with_debug,
            "withDefaultCookieJar": self.with_default_cookie_jar,
            "withoutCookieJar": self.without_cookie_jar,
            "withRandomTLSExtensionOrder": self.with_random_tls_extension_order
        }


"""
{
  "disableKeepAlives": false,
  "disableCompression": false,
  "maxIdleConns": 0,
  "maxIdleConnsPerHost": 0,
  "maxConnsPerHost": 0,
  "maxResponseHeaderBytes": 0,
  "writeBufferSize": 0,
  "readBufferSize": 0,
  "idleConnTimeout": 0,
}
"""


class TransportOptions:
    def __init__(
            self,
            disable_keep_alives: bool = False,
            disable_compression: bool = False,
            max_idle_conns: int = 0,
            max_idle_conns_per_host: int = 0,
            max_conns_per_host: int = 0,
            max_response_header_bytes: int = 0,
            write_buffer_size: int = 0,
            read_buffer_size: int = 0,
            idle_conn_timeout: int = 0,
    ):
        self.disable_keep_alives = disable_keep_alives
        self.disable_compression = disable_compression
        self.max_idle_conns = max_idle_conns
        self.max_idle_conns_per_host = max_idle_conns_per_host
        self.max_conns_per_host = max_conns_per_host
        self.max_response_header_bytes = max_response_header_bytes
        self.write_buffer_size = write_buffer_size
        self.read_buffer_size = read_buffer_size
        self.idle_conn_timeout = idle_conn_timeout

    def to_payload(self):
        return {
            "disableKeepAlives": self.disable_keep_alives,
            "disableCompression": self.disable_compression,
            "maxIdleConns": self.max_idle_conns,
            "maxIdleConnsPerHost": self.max_conns_per_host,
            "maxConnsPerHost": self.max_conns_per_host,
            "maxResponseHeaderBytes": self.max_response_header_bytes,
            "writeBufferSize": self.write_buffer_size,
            "readBufferSize": self.read_buffer_size,
            "idleConnTimeout": self.idle_conn_timeout,
        }
