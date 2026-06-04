# HTTPX Comprehensive Reference

A complete reference for building with HTTPX — covering every class, function signature, parameter type, and pattern in the library. Built from the source code of the HTTPX 0.28.1 repository.

---

## Table of Contents

- [1. Top-Level API Functions](#1-top-level-api-functions)
- [2. Client (Synchronous)](#2-client-synchronous)
- [3. AsyncClient](#3-asyncclient)
- [4. Request Object](#4-request-object)
- [5. Response Object](#5-response-object)
- [6. URL Object](#6-url-object)
- [7. Headers Object](#7-headers-object)
- [8. Cookies Object](#8-cookies-object)
- [9. QueryParams Object](#9-queryparams-object)
- [10. Timeout Configuration](#10-timeout-configuration)
- [11. Limits (Connection Pool)](#11-limits-connection-pool)
- [12. Proxy Configuration](#12-proxy-configuration)
- [13. SSL Configuration](#13-ssl-configuration)
- [14. Authentication](#14-authentication)
- [15. Event Hooks](#15-event-hooks)
- [16. Streaming](#16-streaming)
- [17. File Uploads](#17-file-uploads)
- [18. HTTP/2 Support](#18-http2-support)
- [19. Transports](#19-transports)
- [20. Exceptions](#20-exceptions)
- [21. Environment Variables](#21-environment-variables)
- [22. Logging](#22-logging)
- [23. Text Encodings](#23-text-encodings)
- [24. Status Codes](#24-status-codes)
- [25. Common Patterns](#25-common-patterns)

---

## 1. Top-Level API Functions

**Import:** `import httpx`

**Source:** `httpx/_api.py`

### `httpx.request()`

```python
httpx.request(
    method: str,
    url: URL | str,
    *,
    params: QueryParamTypes | None = None,
    content: RequestContent | None = None,
    data: RequestData | None = None,
    files: RequestFiles | None = None,
    json: Any | None = None,
    headers: HeaderTypes | None = None,
    cookies: CookieTypes | None = None,
    auth: AuthTypes | None = None,
    proxy: ProxyTypes | None = None,
    timeout: TimeoutTypes = DEFAULT_TIMEOUT_CONFIG,  # 5.0 seconds
    follow_redirects: bool = False,
    verify: ssl.SSLContext | str | bool = True,
    trust_env: bool = True,
) -> Response
```

### `httpx.stream()`

```python
httpx.stream(
    method: str,
    url: URL | str,
    *,
    params: QueryParamTypes | None = None,
    content: RequestContent | None = None,
    data: RequestData | None = None,
    files: RequestFiles | None = None,
    json: Any | None = None,
    headers: HeaderTypes | None = None,
    cookies: CookieTypes | None = None,
    auth: AuthTypes | None = None,
    proxy: ProxyTypes | None = None,
    timeout: TimeoutTypes = DEFAULT_TIMEOUT_CONFIG,
    follow_redirects: bool = False,
    verify: ssl.SSLContext | str | bool = True,
    trust_env: bool = True,
) -> typing.Iterator[Response]
```

Used as a context manager:

```python
with httpx.stream("GET", "https://example.com") as response:
    for chunk in response.iter_bytes():
        print(chunk)
```

### HTTP Method Shortcuts

All shortcut functions accept the same keyword arguments as `httpx.request()`.

```python
httpx.get(url, *, params, headers, cookies, auth, proxy, follow_redirects, verify, timeout, trust_env) -> Response
httpx.post(url, *, content, data, files, json, params, headers, cookies, auth, proxy, follow_redirects, verify, timeout, trust_env) -> Response
httpx.put(url, *, content, data, files, json, params, headers, cookies, auth, proxy, follow_redirects, verify, timeout, trust_env) -> Response
httpx.patch(url, *, content, data, files, json, params, headers, cookies, auth, proxy, follow_redirects, verify, timeout, trust_env) -> Response
httpx.delete(url, *, params, headers, cookies, auth, proxy, follow_redirects, timeout, verify, trust_env) -> Response
httpx.head(url, *, params, headers, cookies, auth, proxy, follow_redirects, verify, timeout, trust_env) -> Response
httpx.options(url, *, params, headers, cookies, auth, proxy, follow_redirects, verify, timeout, trust_env) -> Response
```

### Usage

```python
import httpx

# Simple GET
response = httpx.get("https://httpbin.org/get")
print(response.status_code)  # 200
print(response.json())

# POST with JSON body
response = httpx.post("https://httpbin.org/post", json={"key": "value"})

# POST with form data
response = httpx.post("https://httpbin.org/post", data={"key": "value"})

# Custom headers
response = httpx.get("https://example.com", headers={"Authorization": "Bearer token123"})

# Query parameters
response = httpx.get("https://httpbin.org/get", params={"page": 1, "limit": 10})

# Follow redirects (disabled by default)
response = httpx.get("http://github.com", follow_redirects=True)
```

---

## 2. Client (Synchronous)

**Import:** `from httpx import Client`

**Source:** `httpx/_client.py`

### Constructor

```python
client = Client(
    *,
    auth: AuthTypes | None = None,
    params: QueryParamTypes | None = None,
    headers: HeaderTypes | None = None,
    cookies: CookieTypes | None = None,
    verify: ssl.SSLContext | str | bool = True,
    cert: CertTypes | None = None,
    trust_env: bool = True,
    http1: bool = True,
    http2: bool = False,
    proxy: ProxyTypes | None = None,
    mounts: None | Mapping[str, BaseTransport | None] = None,
    timeout: TimeoutTypes = DEFAULT_TIMEOUT_CONFIG,  # 5.0 seconds
    follow_redirects: bool = False,
    limits: Limits = DEFAULT_LIMITS,  # max_connections=100, max_keepalive_connections=20
    max_redirects: int = DEFAULT_MAX_REDIRECTS,  # 20
    event_hooks: None | Mapping[str, list[EventHook]] = None,
    base_url: URL | str = "",
    transport: BaseTransport | None = None,
    default_encoding: str | Callable[[bytes], str] = "utf-8",
)
```

### Key Parameters

| Parameter | Description |
|-----------|-------------|
| `auth` | Default authentication for all requests |
| `params` | Default query parameters merged into all requests |
| `headers` | Default headers merged into all requests |
| `cookies` | Default cookies merged into all requests |
| `verify` | SSL verification: `True`, `False`, or `ssl.SSLContext` |
| `cert` | Client-side SSL certificate |
| `http2` | Enable HTTP/2 support (requires `httpx[http2]`) |
| `proxy` | Proxy URL for all requests |
| `mounts` | Transport routing map for URL pattern matching |
| `timeout` | Default timeout configuration (default: 5 seconds) |
| `follow_redirects` | Follow redirects by default (default: `False`) |
| `limits` | Connection pool limits |
| `max_redirects` | Maximum number of redirects to follow (default: 20) |
| `event_hooks` | Dict of `"request"` and `"response"` hook lists |
| `base_url` | Base URL prepended to all relative request URLs |
| `transport` | Custom transport implementation |
| `default_encoding` | Encoding for response text (default: `"utf-8"`) |

### Key Methods

```python
# HTTP methods — same kwargs as top-level API plus extensions
client.get(url, *, params, headers, cookies, auth, follow_redirects, timeout, extensions) -> Response
client.post(url, *, content, data, files, json, params, headers, cookies, auth, follow_redirects, timeout, extensions) -> Response
client.put(url, *, content, data, files, json, params, headers, cookies, auth, follow_redirects, timeout, extensions) -> Response
client.patch(url, *, content, data, files, json, params, headers, cookies, auth, follow_redirects, timeout, extensions) -> Response
client.delete(url, *, params, headers, cookies, auth, follow_redirects, timeout, extensions) -> Response
client.head(url, *, params, headers, cookies, auth, follow_redirects, timeout, extensions) -> Response
client.options(url, *, params, headers, cookies, auth, follow_redirects, timeout, extensions) -> Response

# Generic request
client.request(method, url, *, content, data, files, json, params, headers, cookies, auth, follow_redirects, timeout, extensions) -> Response

# Streaming (context manager)
client.stream(method, url, *, content, data, files, json, params, headers, cookies, auth, follow_redirects, timeout, extensions) -> Iterator[Response]

# Build a Request without sending
client.build_request(method, url, *, content, data, files, json, params, headers, cookies, timeout, extensions) -> Request

# Send a pre-built Request
client.send(request, *, stream, auth, follow_redirects) -> Response

# Close the client
client.close() -> None
```

### Key Properties

| Property | Type | Description |
|----------|------|-------------|
| `is_closed` | `bool` | Whether the client has been closed |
| `timeout` | `Timeout` | Current timeout configuration (read-write) |
| `auth` | `Auth \| None` | Current authentication (read-write) |
| `base_url` | `URL` | Current base URL (read-write) |
| `headers` | `Headers` | Current default headers (read-write) |
| `cookies` | `Cookies` | Current cookies (read-write) |
| `params` | `QueryParams` | Current default query params (read-write) |
| `event_hooks` | `dict` | Current event hooks (read-write) |
| `trust_env` | `bool` | Whether environment variables are used |

### Usage

```python
import httpx

# Recommended: use as context manager
with httpx.Client() as client:
    response = client.get("https://example.com")

# With base URL
with httpx.Client(base_url="https://api.example.com/v1") as client:
    response = client.get("/users")  # GET https://api.example.com/v1/users

# With default headers and auth
with httpx.Client(
    headers={"User-Agent": "my-app/1.0"},
    auth=("username", "password"),
) as client:
    response = client.get("https://example.com/protected")

# Configuration merging: headers, params, cookies are COMBINED;
# all other settings use request-level values over client-level
with httpx.Client(headers={"X-Client": "app"}) as client:
    response = client.get(
        "https://example.com",
        headers={"X-Request": "specific"},
    )
    # Both X-Client and X-Request headers are sent
```

---

## 3. AsyncClient

**Import:** `from httpx import AsyncClient`

**Source:** `httpx/_client.py`

### Constructor

Same parameters as `Client`, except `transport` accepts `AsyncBaseTransport` and `mounts` maps to `AsyncBaseTransport | None`.

### Key Methods

All request methods are `async`. The streaming context manager is also async.

```python
# HTTP methods
await client.get(url, **kwargs) -> Response
await client.post(url, **kwargs) -> Response
await client.put(url, **kwargs) -> Response
await client.patch(url, **kwargs) -> Response
await client.delete(url, **kwargs) -> Response
await client.head(url, **kwargs) -> Response
await client.options(url, **kwargs) -> Response

# Generic request
await client.request(method, url, **kwargs) -> Response

# Streaming (async context manager)
async with client.stream(method, url, **kwargs) as response: ...

# Build a Request without sending
client.build_request(method, url, **kwargs) -> Request  # not async

# Send a pre-built Request
await client.send(request, *, stream, auth, follow_redirects) -> Response

# Close the client
await client.aclose() -> None
```

### Usage

```python
import asyncio
import httpx

async def main():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://www.example.com/")
        print(response.status_code)

asyncio.run(main())

# Async streaming
async with httpx.AsyncClient() as client:
    async with client.stream("GET", "https://www.example.com/") as response:
        async for chunk in response.aiter_bytes():
            print(chunk)

# Event hooks for async clients must be async functions
async def log_request(request):
    print(f"Request: {request.method} {request.url}")

async def log_response(response):
    print(f"Response: {response.status_code}")

async with httpx.AsyncClient(event_hooks={
    "request": [log_request],
    "response": [log_response],
}) as client:
    await client.get("https://example.com")
```

---

## 4. Request Object

**Import:** `from httpx import Request`

**Source:** `httpx/_models.py`

### Constructor

```python
request = Request(
    method: str,
    url: URL | str,
    *,
    params: QueryParamTypes | None = None,
    headers: HeaderTypes | None = None,
    cookies: CookieTypes | None = None,
    content: RequestContent | None = None,
    data: RequestData | None = None,
    files: RequestFiles | None = None,
    json: Any | None = None,
    stream: SyncByteStream | AsyncByteStream | None = None,
    extensions: RequestExtensions | None = None,
)
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `method` | `str` | HTTP method |
| `url` | `URL` | Request URL |
| `headers` | `Headers` | Request headers |
| `extensions` | `dict` | Request extensions |
| `content` | `bytes` | Body content (raises `RequestNotRead` if not read) |

### Methods

```python
request.read() -> bytes       # Read body synchronously
await request.aread() -> bytes  # Read body asynchronously
```

### Usage

```python
import httpx

# Build and send a request manually
request = httpx.Request("GET", "https://example.com", headers={"Host": "example.com"})
with httpx.Client() as client:
    response = client.send(request)

# Build request with client (applies client defaults)
with httpx.Client(headers={"X-Api-Key": "secret"}) as client:
    request = client.build_request("GET", "https://api.example.com")
    # request.headers includes X-Api-Key
    del request.headers["X-Api-Key"]  # modify before sending
    response = client.send(request)
```

---

## 5. Response Object

**Import:** `from httpx import Response`

**Source:** `httpx/_models.py`

### Constructor

```python
response = Response(
    status_code: int,
    *,
    headers: HeaderTypes | None = None,
    content: ResponseContent | None = None,
    text: str | None = None,
    html: str | None = None,
    json: Any = None,
    stream: SyncByteStream | AsyncByteStream | None = None,
    request: Request | None = None,
    extensions: ResponseExtensions | None = None,
    history: list[Response] | None = None,
    default_encoding: str | Callable[[bytes], str] = "utf-8",
)
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `status_code` | `int` | HTTP status code |
| `reason_phrase` | `str` | HTTP reason text |
| `http_version` | `str` | `"HTTP/1.0"`, `"HTTP/1.1"`, or `"HTTP/2"` |
| `url` | `URL` | Request URL |
| `headers` | `Headers` | Response headers |
| `content` | `bytes` | Response body as bytes (raises `ResponseNotRead` if not read) |
| `text` | `str` | Response body decoded as text |
| `encoding` | `str \| None` | Character encoding (read-write) |
| `charset_encoding` | `str \| None` | Encoding from Content-Type header |
| `request` | `Request` | The originating request (read-write) |
| `elapsed` | `timedelta` | Time between send and response receipt (read-write) |
| `cookies` | `Cookies` | Response cookies |
| `history` | `list[Response]` | Redirect history |
| `next_request` | `Request \| None` | Next redirect request if available |
| `num_bytes_downloaded` | `int` | Bytes received so far (streaming) |
| `is_closed` | `bool` | Whether the response stream is closed |
| `is_stream_consumed` | `bool` | Whether the stream has been fully read |
| `links` | `dict` | Parsed Link headers |
| `extensions` | `dict` | Response extensions (e.g., `http_version`, `network_stream`) |

### Status Check Properties

| Property | Type | Description |
|----------|------|-------------|
| `is_informational` | `bool` | 1xx status codes |
| `is_success` | `bool` | 2xx status codes |
| `is_redirect` | `bool` | 3xx status codes |
| `is_client_error` | `bool` | 4xx status codes |
| `is_server_error` | `bool` | 5xx status codes |
| `is_error` | `bool` | 4xx or 5xx status codes |
| `has_redirect_location` | `bool` | Has a Location header for redirects |

### Methods

```python
# Status checking
response.raise_for_status() -> Response  # raises HTTPStatusError for 4xx/5xx; returns self for chaining

# Parsing
response.json(**kwargs) -> Any  # Parse body as JSON

# Reading body
response.read() -> bytes
await response.aread() -> bytes

# Streaming iterators (sync)
response.iter_bytes(chunk_size: int | None = None) -> Iterator[bytes]
response.iter_text(chunk_size: int | None = None) -> Iterator[str]
response.iter_lines() -> Iterator[str]
response.iter_raw(chunk_size: int | None = None) -> Iterator[bytes]  # undecompressed

# Streaming iterators (async)
response.aiter_bytes(chunk_size: int | None = None) -> AsyncIterator[bytes]
response.aiter_text(chunk_size: int | None = None) -> AsyncIterator[str]
response.aiter_lines() -> AsyncIterator[str]
response.aiter_raw(chunk_size: int | None = None) -> AsyncIterator[bytes]

# Closing
response.close() -> None
await response.aclose() -> None
```

### Usage

```python
import httpx

response = httpx.get("https://httpbin.org/get")

# Status
print(response.status_code)        # 200
print(response.is_success)         # True

# Body access
print(response.text)               # decoded string
print(response.content)            # raw bytes
print(response.json())             # parsed JSON

# Chaining with raise_for_status
data = httpx.get("https://api.example.com/data").raise_for_status().json()

# Redirect info
response = httpx.get("http://github.com/")
print(response.status_code)        # 301
print(response.next_request)       # <Request('GET', 'https://github.com/')>

response = httpx.get("http://github.com/", follow_redirects=True)
print(response.history)            # [<Response [301 Moved Permanently]>]
```

---

## 6. URL Object

**Import:** `from httpx import URL`

**Source:** `httpx/_urls.py`

### Constructor

```python
url = URL(url: URL | str = "", params: QueryParamTypes | None = None)
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `scheme` | `str` | URL scheme (e.g., `"https"`) |
| `authority` | `str` | Authority component (e.g., `"example.org"`) |
| `host` | `str` | Hostname |
| `port` | `int \| None` | Port number |
| `path` | `str` | URL path |
| `query` | `bytes` | Raw query string |
| `params` | `QueryParams` | Parsed query parameters |
| `raw_path` | `bytes` | URL-encoded path |
| `fragment` | `str` | URL fragment |
| `is_ssl` | `bool` | Whether scheme is HTTPS |
| `is_absolute_url` | `bool` | Whether URL is absolute |
| `is_relative_url` | `bool` | Whether URL is relative |

### Methods

```python
url.copy_with(**kwargs) -> URL  # Return modified copy
```

### Usage

```python
import httpx

url = httpx.URL("https://example.org:8080/path?query=value#fragment")
print(url.scheme)    # "https"
print(url.host)      # "example.org"
print(url.port)      # 8080
print(url.path)      # "/path"
print(url.is_ssl)    # True
```

---

## 7. Headers Object

**Import:** `from httpx import Headers`

**Source:** `httpx/_models.py`

### Constructor

```python
headers = Headers(
    headers: HeaderTypes | None = None,
    encoding: str | None = None,
)
```

### Key Methods

```python
headers.get(key: str, default=None)                       # Case-insensitive lookup
headers.get_list(key: str, split_commas: bool = False)     # All values for a key
headers.multi_items() -> list[tuple[str, str]]             # All key-value pairs
headers.update(headers: HeaderTypes | None = None)
headers.copy() -> Headers
```

Headers implements `MutableMapping` with **case-insensitive** key access.

### Usage

```python
import httpx

headers = httpx.Headers({"Content-Type": "application/json", "Accept": "text/html"})
print(headers["content-type"])  # "application/json" (case-insensitive)
```

---

## 8. Cookies Object

**Import:** `from httpx import Cookies`

**Source:** `httpx/_models.py`

### Constructor

```python
cookies = Cookies(cookies: CookieTypes | None = None)
```

### Key Methods

```python
cookies.set(name, value, domain=None, path="/")
cookies.get(name, default=None, domain=None, path=None)
cookies.delete(name, domain=None, path=None)
cookies.clear(domain=None, path=None)
cookies.jar  # Access the underlying CookieJar
```

Implements `MutableMapping[str, str]`.

### Usage

```python
import httpx

cookies = httpx.Cookies()
cookies.set("session", "abc123", domain="example.org")
cookies.set("other", "xyz", domain="other.org")

# Only matching domain cookies are sent
response = httpx.get("http://example.org/", cookies=cookies)
```

---

## 9. QueryParams Object

**Import:** `from httpx import QueryParams`

**Source:** `httpx/_urls.py`

### Constructor

```python
params = QueryParams(params: QueryParamTypes | None = None)
```

### Key Methods

```python
params.get(key: str, default=None)
params.get_list(key: str) -> list[str]        # All values for a key
params.multi_items() -> list[tuple[str, str]]  # All key-value pairs
params.set(key: str, value) -> QueryParams     # Return new instance with key set
params.add(key: str, value) -> QueryParams     # Return new instance with key added
params.remove(key: str) -> QueryParams         # Return new instance with key removed
params.merge(other) -> QueryParams             # Return merged instance
```

`QueryParams` is **immutable** — all modification methods return new instances.

### Usage

```python
import httpx

params = httpx.QueryParams({"page": 1})
params = params.add("tag", "python")
params = params.add("tag", "http")
print(str(params))  # "page=1&tag=python&tag=http"
```

---

## 10. Timeout Configuration

**Import:** `from httpx import Timeout`

**Source:** `httpx/_config.py`

### Constructor

```python
timeout = Timeout(
    timeout: float | None = UNSET,  # Default for all operations
    *,
    connect: float | None = UNSET,
    read: float | None = UNSET,
    write: float | None = UNSET,
    pool: float | None = UNSET,
)
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `connect` | `float \| None` | Timeout for establishing a connection |
| `read` | `float \| None` | Timeout for receiving response data |
| `write` | `float \| None` | Timeout for sending request data |
| `pool` | `float \| None` | Timeout for acquiring a connection from the pool |

### Methods

```python
timeout.as_dict() -> dict[str, float | None]
```

### Default

```python
DEFAULT_TIMEOUT_CONFIG = Timeout(timeout=5.0)  # 5 seconds for all operations
```

### Usage

```python
import httpx

# Single value for all operations
client = httpx.Client(timeout=10.0)

# Disable timeouts
client = httpx.Client(timeout=None)

# Fine-grained control
timeout = httpx.Timeout(10.0, connect=60.0)
client = httpx.Client(timeout=timeout)

# Per-request override
response = client.get("https://example.com", timeout=30.0)
```

---

## 11. Limits (Connection Pool)

**Import:** `from httpx import Limits`

**Source:** `httpx/_config.py`

### Constructor

```python
limits = Limits(
    *,
    max_connections: int | None = None,
    max_keepalive_connections: int | None = None,
    keepalive_expiry: float | None = 5.0,
)
```

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_connections` | `100` | Maximum total connections (`None` = unlimited) |
| `max_keepalive_connections` | `20` | Max keep-alive connections (`None` = unlimited) |
| `keepalive_expiry` | `5.0` | Seconds before idle connections are closed (`None` = no limit) |

### Default

```python
DEFAULT_LIMITS = Limits(max_connections=100, max_keepalive_connections=20)
```

### Usage

```python
import httpx

limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
client = httpx.Client(limits=limits)
```

---

## 12. Proxy Configuration

**Import:** `from httpx import Proxy`

**Source:** `httpx/_config.py`

### Constructor

```python
proxy = Proxy(
    url: URL | str,
    *,
    ssl_context: ssl.SSLContext | None = None,
    auth: tuple[str, str] | None = None,
    headers: HeaderTypes | None = None,
)
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `url` | `URL` | Proxy URL |
| `auth` | `tuple[str, str] \| None` | Proxy authentication credentials |
| `headers` | `Headers` | Custom proxy headers |
| `ssl_context` | `ssl.SSLContext \| None` | SSL context for proxy connection |
| `raw_auth` | `tuple[bytes, bytes] \| None` | Raw auth bytes |

### Usage

```python
import httpx

# Simple proxy for all requests
with httpx.Client(proxy="http://localhost:8030") as client:
    response = client.get("https://example.com")

# Proxy with authentication
with httpx.Client(proxy="http://user:pass@localhost:8030") as client:
    response = client.get("https://example.com")

# Different proxies per protocol using mounts
proxy_mounts = {
    "http://": httpx.HTTPTransport(proxy="http://localhost:8030"),
    "https://": httpx.HTTPTransport(proxy="http://localhost:8031"),
}
with httpx.Client(mounts=proxy_mounts) as client:
    response = client.get("https://example.com")

# No-proxy bypass for specific domains
mounts = {
    "all://": httpx.HTTPTransport(proxy="http://localhost:8030"),
    "all://example.com": None,  # bypass proxy
}

# SOCKS proxy (requires pip install httpx[socks])
client = httpx.Client(proxy="socks5://user:pass@host:port")
```

### Mount Routing Patterns

| Pattern | Description |
|---------|-------------|
| `"all://"` | All requests |
| `"http://"` | HTTP requests only |
| `"https://"` | HTTPS requests only |
| `"all://example.com"` | Exact domain |
| `"all://*example.com"` | Domain and subdomains |
| `"all://*.example.com"` | Subdomains only |
| `"all://*:1234"` | All requests on specific port |
| `"https://example.com:1234"` | Specific domain, scheme, and port |

---

## 13. SSL Configuration

**Source:** `httpx/_config.py`

### `create_ssl_context()`

```python
httpx.create_ssl_context(
    verify: ssl.SSLContext | str | bool = True,
    cert: CertTypes | None = None,
    trust_env: bool = True,
) -> ssl.SSLContext
```

### Usage

```python
import httpx
import ssl

# Default: verify SSL certificates
response = httpx.get("https://example.com")

# Disable verification (insecure)
response = httpx.get("https://example.com", verify=False)

# Custom CA bundle
response = httpx.get("https://example.com", verify="/path/to/ca-bundle.crt")

# Custom SSL context
ctx = ssl.create_default_context()
ctx.load_cert_chain(certfile="client.pem", keyfile="client.key")
client = httpx.Client(verify=ctx)

# Using truststore for system certificate store
import truststore
ctx = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
client = httpx.Client(verify=ctx)
```

---

## 14. Authentication

**Import:** `from httpx import BasicAuth, DigestAuth, NetRCAuth, Auth, FunctionAuth`

**Source:** `httpx/_auth.py`

### BasicAuth

```python
auth = BasicAuth(username: str | bytes, password: str | bytes)
```

### DigestAuth

```python
auth = DigestAuth(username: str | bytes, password: str | bytes)
```

### NetRCAuth

```python
auth = NetRCAuth(file: str | None = None)  # defaults to ~/.netrc
```

### FunctionAuth

```python
auth = FunctionAuth(func: Callable[[Request], Request])
```

### Custom Auth (Base Class)

```python
class Auth:
    requires_request_body: bool = False
    requires_response_body: bool = False

    def auth_flow(self, request: Request) -> Generator[Request, Response, None]: ...
    def sync_auth_flow(self, request: Request) -> Generator[Request, Response, None]: ...
    async def async_auth_flow(self, request: Request) -> AsyncGenerator[Request, Response]: ...
```

### Usage

```python
import httpx

# Tuple shorthand for BasicAuth
response = httpx.get("https://example.com", auth=("user", "pass"))

# Explicit BasicAuth
client = httpx.Client(auth=httpx.BasicAuth("user", "pass"))

# Digest authentication
client = httpx.Client(auth=httpx.DigestAuth("user", "pass"))

# NetRC file
client = httpx.Client(auth=httpx.NetRCAuth())

# Custom auth class
class TokenAuth(httpx.Auth):
    def __init__(self, token: str):
        self.token = token

    def auth_flow(self, request):
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request

client = httpx.Client(auth=TokenAuth("my-token"))

# Custom auth with response handling (e.g., token refresh)
class RefreshableTokenAuth(httpx.Auth):
    def __init__(self, access_token, refresh_token, refresh_url):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.refresh_url = refresh_url

    def auth_flow(self, request):
        request.headers["Authorization"] = f"Bearer {self.access_token}"
        response = yield request

        if response.status_code == 401:
            # Refresh token and retry
            refresh_response = yield httpx.Request("POST", self.refresh_url, json={"refresh": self.refresh_token})
            self.access_token = refresh_response.json()["access_token"]
            request.headers["Authorization"] = f"Bearer {self.access_token}"
            yield request
```

---

## 15. Event Hooks

Event hooks allow you to install callbacks that are called on every request or response.

### Hook Types

| Hook | Signature | Called When |
|------|-----------|------------|
| `"request"` | `(request: Request) -> None` | After request is prepared, before sending |
| `"response"` | `(response: Response) -> None` | After response is received, before returning |

### Usage

```python
import httpx

def log_request(request):
    print(f"Request: {request.method} {request.url}")

def log_response(response):
    print(f"Response: {response.status_code}")

def raise_on_4xx_5xx(response):
    response.raise_for_status()

# Set via constructor
client = httpx.Client(event_hooks={
    "request": [log_request],
    "response": [log_response, raise_on_4xx_5xx],
})

# Set via property
client = httpx.Client()
client.event_hooks["request"] = [log_request]
client.event_hooks["response"] = [log_response]

# Async clients require async hook functions
async def async_log_request(request):
    print(f"Request: {request.method} {request.url}")

async with httpx.AsyncClient(event_hooks={"request": [async_log_request]}) as client:
    await client.get("https://example.com")
```

**Important:** If you need the response body inside a hook, call `response.read()` (sync) or `await response.aread()` (async).

---

## 16. Streaming

### Synchronous Streaming

```python
import httpx

# Top-level API
with httpx.stream("GET", "https://example.com/large-file") as response:
    for chunk in response.iter_bytes():
        process(chunk)

# Client API
with httpx.Client() as client:
    with client.stream("GET", "https://example.com/large-file") as response:
        for chunk in response.iter_bytes():
            process(chunk)
```

### Async Streaming

```python
async with httpx.AsyncClient() as client:
    async with client.stream("GET", "https://example.com/large-file") as response:
        async for chunk in response.aiter_bytes():
            process(chunk)
```

### Streaming Iterators

| Sync Method | Async Method | Description |
|-------------|-------------|-------------|
| `iter_bytes(chunk_size)` | `aiter_bytes(chunk_size)` | Iterate over decompressed bytes |
| `iter_text(chunk_size)` | `aiter_text(chunk_size)` | Iterate over decoded text |
| `iter_lines()` | `aiter_lines()` | Iterate over text lines |
| `iter_raw(chunk_size)` | `aiter_raw(chunk_size)` | Iterate over raw (undecompressed) bytes |

### Conditional Reading

```python
with httpx.stream("GET", url) as response:
    content_length = int(response.headers.get("Content-Length", 0))
    if content_length < MAX_SIZE:
        response.read()
        print(response.text)
```

### Download with Progress

```python
import httpx
from tqdm import tqdm

with httpx.stream("GET", url) as response:
    total = int(response.headers["Content-Length"])
    with tqdm(total=total, unit_scale=True, unit_divisor=1024, unit="B") as progress:
        num_bytes = response.num_bytes_downloaded
        for chunk in response.iter_bytes():
            file.write(chunk)
            progress.update(response.num_bytes_downloaded - num_bytes)
            num_bytes = response.num_bytes_downloaded
```

---

## 17. File Uploads

### Single File

```python
import httpx

with open("report.xls", "rb") as f:
    files = {"upload-file": f}
    response = httpx.post("https://httpbin.org/post", files=files)
```

### File with Explicit MIME Type

```python
with open("report.xls", "rb") as f:
    files = {"upload-file": ("report.xls", f, "application/vnd.ms-excel")}
    response = httpx.post("https://httpbin.org/post", files=files)
```

### Multiple Files

```python
with open("foo.png", "rb") as foo, open("bar.png", "rb") as bar:
    files = [
        ("images", ("foo.png", foo, "image/png")),
        ("images", ("bar.png", bar, "image/png")),
    ]
    response = httpx.post("https://httpbin.org/post", files=files)
```

### Files with Form Data

```python
data = {"message": "Hello, world!"}
with open("report.xls", "rb") as f:
    files = {"file": f}
    response = httpx.post("https://httpbin.org/post", data=data, files=files)
```

### File Types

```python
# Supported file value formats:
files = {"field": file_object}                                    # file-like object
files = {"field": ("filename.txt", file_object)}                  # (filename, file)
files = {"field": ("filename.txt", file_object, "text/plain")}   # (filename, file, content_type)
files = {"field": ("filename.txt", b"raw bytes", "text/plain")}  # (filename, bytes, content_type)
```

---

## 18. HTTP/2 Support

**Install:** `pip install httpx[http2]`

HTTP/2 is **not enabled by default**. It must be explicitly opted in via Client.

```python
import httpx

# Enable HTTP/2 on client
client = httpx.Client(http2=True)
response = client.get("https://www.example.com/")
print(response.http_version)  # "HTTP/2" or "HTTP/1.1" (fallback)

# Async client
async with httpx.AsyncClient(http2=True) as client:
    response = await client.get("https://www.example.com/")
```

**Key points:**
- HTTP/2 requires the `h2` package (`httpx[http2]`)
- Both client and server must support HTTP/2
- Falls back to HTTP/1.1 if server doesn't support it
- Provides multiplexing (concurrent requests over one connection)
- Automatic header compression (HPACK)
- HTTP/2 is **not available** via top-level functions (`httpx.get()` etc.) — only via `Client`/`AsyncClient`

---

## 19. Transports

**Import:** `from httpx import HTTPTransport, AsyncHTTPTransport, WSGITransport, ASGITransport, MockTransport, BaseTransport, AsyncBaseTransport`

**Source:** `httpx/_transports/`

### HTTPTransport

```python
transport = HTTPTransport(
    proxy: ProxyTypes | None = None,
    local_address: str | None = None,
    retries: int = 0,              # Retry on ConnectError/ConnectTimeout
    uds: str | None = None,       # Unix domain socket path
    http2: bool = False,
)
client = httpx.Client(transport=transport)
```

### AsyncHTTPTransport

Same parameters as `HTTPTransport`, for use with `AsyncClient`.

### WSGITransport (Testing WSGI Apps)

```python
transport = WSGITransport(
    app: Callable,                   # WSGI application
    raise_app_exceptions: bool = True,
    script_name: str = "",           # Mount app at subpath
    remote_addr: str = "127.0.0.1",  # Simulated client IP
)
```

```python
from flask import Flask
import httpx

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

transport = httpx.WSGITransport(app=app)
with httpx.Client(transport=transport, base_url="http://testserver") as client:
    response = client.get("/")
    assert response.text == "Hello World!"
```

### ASGITransport (Testing ASGI Apps)

```python
transport = ASGITransport(
    app: Callable,                   # ASGI application
    raise_app_exceptions: bool = True,
    root_path: str = "",             # ASGI root_path
    client: tuple[str, int] = ("127.0.0.1", 123),  # Simulated client address
)
```

```python
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Route
import httpx

async def hello(request):
    return HTMLResponse("Hello World!")

app = Starlette(routes=[Route("/", hello)])

transport = httpx.ASGITransport(app=app)
async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
    response = await client.get("/")
    assert response.text == "Hello World!"
```

### MockTransport (Testing)

```python
import httpx

def handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json={"message": "Hello"})

transport = httpx.MockTransport(handler)
client = httpx.Client(transport=transport)
response = client.get("https://example.com")

# Mock specific domains with mounts
mounts = {
    "all://api.example.com": httpx.MockTransport(handler),
}
client = httpx.Client(mounts=mounts)
```

### Custom Transport

```python
import httpx

class MyTransport(httpx.BaseTransport):
    def handle_request(self, request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"text": "Hello, world!"})

class MyAsyncTransport(httpx.AsyncBaseTransport):
    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"text": "Hello, world!"})
```

### Mounting Transports

```python
import httpx

# Different transport configs per domain
mounts = {
    "all://": httpx.HTTPTransport(http2=True),
    "all://*example.org": httpx.HTTPTransport(),  # HTTP/1.1 only for this domain
}
client = httpx.Client(mounts=mounts)

# HTTPS redirect transport
class HTTPSRedirect(httpx.BaseTransport):
    def handle_request(self, request):
        url = request.url.copy_with(scheme="https")
        return httpx.Response(303, headers={"Location": str(url)})

mounts = {
    "http://": HTTPSRedirect(),
    "https://": httpx.HTTPTransport(),
}
client = httpx.Client(mounts=mounts)
```

---

## 20. Exceptions

**Import:** `from httpx import ...`

**Source:** `httpx/_exceptions.py`

### Exception Hierarchy

```
HTTPError
├── RequestError
│   ├── TransportError
│   │   ├── TimeoutException
│   │   │   ├── ConnectTimeout
│   │   │   ├── ReadTimeout
│   │   │   ├── WriteTimeout
│   │   │   └── PoolTimeout
│   │   ├── NetworkError
│   │   │   ├── ConnectError
│   │   │   ├── ReadError
│   │   │   ├── WriteError
│   │   │   └── CloseError
│   │   ├── ProtocolError
│   │   │   ├── LocalProtocolError
│   │   │   └── RemoteProtocolError
│   │   ├── ProxyError
│   │   └── UnsupportedProtocol
│   ├── DecodingError
│   └── TooManyRedirects
└── HTTPStatusError

InvalidURL
CookieConflict
StreamError
├── StreamConsumed
├── StreamClosed
├── ResponseNotRead
└── RequestNotRead
```

### Key Exception Properties

| Exception | Properties |
|-----------|------------|
| `RequestError` | `.request: Request` |
| `HTTPStatusError` | `.request: Request`, `.response: Response` |

### Usage

```python
import httpx

# Catch all HTTP errors
try:
    response = httpx.get("https://example.com")
    response.raise_for_status()
except httpx.HTTPError as exc:
    print(f"Error: {exc}")

# Catch request/transport errors separately
try:
    response = httpx.get("https://example.com")
except httpx.ConnectTimeout:
    print("Connection timed out")
except httpx.ReadTimeout:
    print("Read timed out")
except httpx.NetworkError:
    print("Network error")
except httpx.RequestError as exc:
    print(f"Request error for {exc.request.url}: {exc}")

# Catch HTTP status errors
try:
    response.raise_for_status()
except httpx.HTTPStatusError as exc:
    print(f"HTTP {exc.response.status_code}: {exc.response.text}")
```

---

## 21. Environment Variables

| Variable | Description |
|----------|-------------|
| `HTTP_PROXY` | Proxy URL for HTTP requests |
| `HTTPS_PROXY` | Proxy URL for HTTPS requests |
| `ALL_PROXY` | Proxy URL for all requests |
| `NO_PROXY` | Comma-separated list of hosts to bypass proxy |
| `SSL_CERT_FILE` | Path to CA certificate file |
| `SSL_CERT_DIR` | Directory with OpenSSL-formatted certificate store |

All environment variable usage can be disabled with `trust_env=False`:

```python
client = httpx.Client(trust_env=False)
# or
httpx.get("https://example.com", trust_env=False)
```

---

## 22. Logging

HTTPX uses Python's standard `logging` module with two loggers:

| Logger | Description |
|--------|-------------|
| `httpx` | High-level request/response logging |
| `httpcore` | Low-level network connection logging |

### Usage

```python
import logging
import httpx

# Enable debug logging
logging.basicConfig(
    format="%(levelname)s [%(asctime)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)

httpx.get("https://www.example.com")

# Fine-grained control
LOGGING_CONFIG = {
    "version": 1,
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "http",
            "stream": "ext://sys.stderr",
        }
    },
    "formatters": {
        "http": {
            "format": "%(levelname)s [%(asctime)s] %(name)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "loggers": {
        "httpx": {"handlers": ["default"], "level": "DEBUG"},
        "httpcore": {"handlers": ["default"], "level": "DEBUG"},
    },
}

import logging.config
logging.config.dictConfig(LOGGING_CONFIG)
```

---

## 23. Text Encodings

### Default Behavior

HTTPX uses the `charset` from the `Content-Type` header. If not present, falls back to `"utf-8"` (not ISO-8859-1 like RFC 7231 suggests for `text/` types — this is intentional for better compatibility).

### Setting Encoding

```python
import httpx

# Client-level default encoding
client = httpx.Client(default_encoding="shift-jis")

# Per-response override
response = httpx.get("https://example.com")
response.encoding = "ISO-8859-1"
print(response.text)  # decoded with ISO-8859-1
```

### Auto-Detection

```python
# pip install chardet
# or pip install charset-normalizer
import chardet
import httpx

def autodetect(content: bytes) -> str:
    return chardet.detect(content).get("encoding", "utf-8")

client = httpx.Client(default_encoding=autodetect)
response = client.get("https://example.com")
# encoding auto-detected from response content when not in headers
```

---

## 24. Status Codes

**Import:** `from httpx import codes`

HTTPX provides named constants for HTTP status codes:

```python
import httpx

response = httpx.get("https://example.com")
print(response.status_code == httpx.codes.OK)  # True
print(response.status_code == 200)              # True
```

---

## 25. Common Patterns

### Retry on Connection Errors

```python
import httpx

# Transport-level retries (ConnectError and ConnectTimeout only)
transport = httpx.HTTPTransport(retries=3)
client = httpx.Client(transport=transport)
```

### Binary Request Data

```python
import httpx

# Raw bytes
response = httpx.post("https://example.com", content=b"raw bytes")

# Streaming upload with generator
def upload_chunks():
    yield b"chunk1"
    yield b"chunk2"

response = httpx.post("https://example.com", content=upload_chunks())
```

### Request Extensions

```python
import httpx

# Trace events
def log(event_name, info):
    print(event_name, info)

client = httpx.Client()
response = client.get("https://example.com", extensions={"trace": log})

# SNI hostname override
response = httpx.get(
    "https://185.199.108.153/path",
    headers={"Host": "www.encode.io"},
    extensions={"sni_hostname": "www.encode.io"},
)

# Access network stream info from response
response = httpx.get("https://example.com")
network_stream = response.extensions["network_stream"]
client_addr = network_stream.get_extra_info("client_addr")
server_addr = network_stream.get_extra_info("server_addr")

# SSL info (keep connection open via streaming)
with httpx.stream("GET", "https://example.com") as response:
    ssl_object = response.extensions["network_stream"].get_extra_info("ssl_object")
    print("TLS version:", ssl_object.version())
```

### Unix Domain Sockets

```python
import httpx

transport = httpx.HTTPTransport(uds="/var/run/docker.sock")
client = httpx.Client(transport=transport)
response = client.get("http://docker/v1.40/containers/json")
```

### Sending Pre-Built Requests

```python
import httpx

with httpx.Client(headers={"X-Api-Key": "secret"}) as client:
    request = client.build_request("GET", "https://api.example.com")
    # Inspect or modify before sending
    print(request.headers)
    response = client.send(request)
```

### Type Definitions Reference

```python
# Key type aliases from httpx/_types.py
URLTypes = URL | str
QueryParamTypes = QueryParams | Mapping[str, str | Sequence[str]] | list[tuple[str, str]] | str | bytes
HeaderTypes = Headers | Mapping[str, str] | Mapping[bytes, bytes] | Sequence[tuple[str, str]] | Sequence[tuple[bytes, bytes]]
CookieTypes = Cookies | CookieJar | dict[str, str] | list[tuple[str, str]]
TimeoutTypes = float | None | tuple[float | None, float | None, float | None, float | None] | Timeout
ProxyTypes = URL | str | Proxy
AuthTypes = tuple[str | bytes, str | bytes] | Callable[[Request], Request] | Auth
RequestContent = str | bytes | Iterable[bytes] | AsyncIterable[bytes]
RequestData = Mapping[str, Any]
RequestFiles = Mapping[str, FileTypes] | Sequence[tuple[str, FileTypes]]
CertTypes = str | tuple[str, str] | tuple[str, str, str]
```

---
