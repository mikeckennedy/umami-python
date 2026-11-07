# Authentication

There are two ways to authenticate, and you use exactly one of them at a time. Self-hosted instances take a username and password and return a token. Umami Cloud takes an API key. The package routes requests and sets headers differently in each mode, so the choice matters even though the rest of your code stays the same.


# What needs a credential

| Call | Needs | Why |
|----|----|----|
| [new_event()](../reference/new_event.md#umami.new_event), [new_page_view()](../reference/new_page_view.md#umami.new_page_view), [new_revenue_event()](../reference/new_revenue_event.md#umami.new_revenue_event) | [set_url_base()](../reference/set_url_base.md#umami.set_url_base) or a Cloud key | Umami's `/api/send` endpoint is unauthenticated. |
| [heartbeat()](../reference/heartbeat.md#umami.heartbeat) | [set_url_base()](../reference/set_url_base.md#umami.set_url_base) or a Cloud key | Self-hosted pings `/api/heartbeat`. Cloud calls `/me` with the key. |
| [websites()](../reference/websites.md#umami.websites), [website_stats()](../reference/website_stats.md#umami.website_stats), [active_users()](../reference/active_users.md#umami.active_users) | [login()](../reference/login.md#umami.login) or a Cloud key | These read data and require a token or key. |
| [verify_token()](../reference/verify_token.md#umami.verify_token) | [login()](../reference/login.md#umami.login) or a Cloud key | Returns `False` rather than raising when nothing is set. |

Calling a query function before logging in raises [umami.errors.OperationNotAllowedError](../reference/errors.OperationNotAllowedError.md#umami.errors.OperationNotAllowedError) with the message `Call login() or set_cloud_api_key() before proceeding.`


# Self-hosted: set_url_base and login

``` python
import umami

umami.set_url_base('https://umami.example.com')
login = umami.login('admin', 'super-secret')
print(login.user.username, login.user.isAdmin)
```

[login()](../reference/login.md#umami.login) posts to `/api/auth/login`, stores the returned token in the module, and returns a [LoginResponse](../reference/models.LoginResponse.md#umami.models.LoginResponse) with the token and a [User](../reference/models.User.md#umami.models.User) model. You do not need to keep the return value; every later query call sends the stored token as `Authorization: Bearer <token>`.

Both arguments must be non-empty or [ValidationError](../reference/errors.ValidationError.md#umami.errors.ValidationError) is raised. Wrong credentials come back from the server as a 401 and raise `httpx2.HTTPStatusError`.

Calling [login()](../reference/login.md#umami.login) again replaces the stored token. There is no logout function; the token lives until the process exits or you log in again.


## Tokens expire

Umami login tokens are temporary. A long-running process should expect a query call to start failing with a 401 at some point. [verify_token()](../reference/verify_token.md#umami.verify_token) checks the stored token against the server and never raises:

``` python
if not umami.verify_token():
    umami.login('admin', 'super-secret')
```

`verify_token(check_server=False)` skips the network and only reports whether a credential is present, which is the same answer [is_logged_in()](../reference/is_logged_in.md#umami.is_logged_in) gives.


# Umami Cloud: set_cloud_api_key

``` python
import umami

umami.set_cloud_api_key('your-cloud-api-key', region='eu')  # region is optional
umami.set_website_id('978435e2-7ba1-4337-9860-ec31ece2db60')
umami.set_hostname('example.com')
```

Create the key in the Umami Cloud dashboard under the API keys settings. `region` accepts `'us'`, `'eu'`, or `None`; when omitted, Cloud uses the region of the account that owns the key. Any other value raises [ValidationError](../reference/errors.ValidationError.md#umami.errors.ValidationError), as does a blank key.

In Cloud mode the package changes three things:

- Query and verification calls go to `https://api.umami.is/v1`, with `/eu` or `/us` inserted after `v1` when you pin a region, and carry an `x-umami-api-key` header.
- Events go to `https://cloud.umami.is/api/send` with no credential, because the Cloud ingestion endpoint is public. The region does not affect this host.
- [login()](../reference/login.md#umami.login) and [login_async()](../reference/login_async.md#umami.login_async) raise [OperationNotAllowedError](../reference/errors.OperationNotAllowedError.md#umami.errors.OperationNotAllowedError). The key is the credential, and Cloud has no username and password login.

You do not call [set_url_base()](../reference/set_url_base.md#umami.set_url_base) in Cloud mode. If you do, the value is stored but ignored while the key is set.


# Switching modes

[clear_cloud_api_key()](../reference/clear_cloud_api_key.md#umami.clear_cloud_api_key) removes the key and the region. Everything goes back to self-hosted behaviour: events use `url_base`, and query calls need a login token. A token from a [login()](../reference/login.md#umami.login) made before you switched to Cloud mode is still there, so you do not have to log in again.

[is_logged_in()](../reference/is_logged_in.md#umami.is_logged_in) returns `True` when either a login token or a Cloud key is set. It does not contact the server; use [verify_token()](../reference/verify_token.md#umami.verify_token) for that.


# Keep credentials out of code

Read the password or key from an environment variable or a secrets store at startup, then hand it to [login()](../reference/login.md#umami.login) or [set_cloud_api_key()](../reference/set_cloud_api_key.md#umami.set_cloud_api_key). The package does not read any environment variables itself.

``` python
import os
import umami

umami.set_url_base(os.environ['UMAMI_URL'])
umami.login(os.environ['UMAMI_USER'], os.environ['UMAMI_PASSWORD'])
```

If a login fails, [Troubleshooting](troubleshooting.md#login-and-token-problems) lists the causes.
