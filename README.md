# Umami Analytics Client for Python

Client for privacy-preserving, open source [Umami analytics platform](https://umami.is) based on 
`httpx` and `pydantic`. 

`umami-analytics` is intended for adding custom data to your Umami instance (self-hosted or SaaS). Many umami events can supplied directly from HTML via their `data-*` attributes. However, some cannot. For example, if you have an event that is triggered in your app but doesn't have a clear HTML action you can add custom events. These will appear at the bottom of your Umami analtytics page for a website.

One example is a **purchase-course** event that happens deep inside the Python code rather than in HTML at [Talk Python Training](https://training.talkpython.fm). This is what our events section looks like for a typical weekend day (US Pacific Time):

![](https://raw.githubusercontent.com/mikeckennedy/umami-python/main/readme_resources/events-example.jpg)

## Focused on what you need, not what is offered

The [Umami API is extensive](https://umami.is/docs/api) and much of that is intended for their frontend code to be able to function. You probably don't want or need that. `umami-analytics` only covers the subset that most developers will need for common SaaS actions such as adding [custom events](https://umami.is/docs/event-data). That said, PRs are weclome.

## Core Features

* ➕ **Add a custom event** to your Umami analytics dashboard.
* 📄 **Add a page view** to your Umami analytics dashboard.
* 🌐 List all websites with details that you have registered at Umami.
* 📊 **Get website statistics** including page views, visitors, bounce rate, and more.
* 👥 **Get active users** count for real-time monitoring.
* 💓 **Heartbeat check** to verify Umami server connectivity.
* 🔀 Both **sync** and **async** programming models.
* ⚒️ **Structured data with Pydantic** models for API responses.
* 👩‍💻 **Login / authenticate** for either a self-hosted or SaaS hosted instance of Umami.
* 🥇Set a **default website** for a **simplified API** going forward.
* 🔧 **Enable/disable tracking** for development and testing environments.

## Development and Testing Support

🔧 **Disable tracking in development**: Use `umami.disable()` to disable all event and page view tracking without changing your code. Perfect for development and testing environments where you don't want to pollute your analytics with test data.

```python
import umami

# Configure as usual
umami.set_url_base("https://umami.hostedbyyouorthem.com")
umami.set_website_id('cc726914-8e68-4d1a-4be0-af4ca8933456')
umami.set_hostname('somedomain.com')

# Disable tracking for development/testing
umami.disable()

# These calls will return immediately without sending data to Umami
umami.new_event('test-event')  # No HTTP request made
umami.new_page_view('Test Page', '/test')  # No HTTP request made

# Re-enable when needed (default state is enabled)
umami.enable()
```

When tracking is disabled:
- ✅ **No HTTP requests** are made to your Umami server
- ✅ **API calls still validate** parameters (helps catch configuration issues)
- ✅ **All other functions work normally** (login, websites, stats, etc.)
- ✅ **Functions return appropriate values** for compatibility

See the usage example below for the Python API around these features.

## Async or sync API? You choose

🔀 **Async is supported but not required** for your Python code. For functions that access the network, there is a `func()` and `func_async()` variant that works with Python's `async` and `await`.

## Installation

Just `pip install umami-analytics`

## Usage

```python

import umami

umami.set_url_base("https://umami.hostedbyyouorthem.com")

# Auth is NOT required to send events, but is for other features.
login = umami.login(username, password)

# Skip the need to pass the target website in subsequent calls.
umami.set_website_id('cc726914-8e68-4d1a-4be0-af4ca8933456')
umami.set_hostname('somedomain.com')

# Optional: Disable tracking for development/testing
# umami.disable()  # Uncomment to disable tracking

# List your websites
websites = umami.websites()

# Create a new event in the events section of the dashboards.
event_resp = umami.new_event(
    website_id='a7cd-5d1a-2b33', # Only send if overriding default above
    event_name='Umami-Test',
    title='Umami-Test', # Defaults to event_name if omitted.
    hostname='somedomain.com', # Only send if overriding default above.
    url='/users/actions',
    custom_data={'client': 'umami-tester-v1'},
    referrer='https://some_url')

# Create a new page view in the pages section of the dashboards.
page_view_resp = umami.new_page_view(
    website_id='a7cd-5d1a-2b33', # Only send if overriding default above
    page_title='Umami-Test', # Defaults to event_name if omitted.
    hostname='somedomain.com', # Only send if overriding default above.
    url='/users/actions',
    referrer='https://some_url')

# Get website statistics for a date range
from datetime import datetime, timedelta

end_date = datetime.now()
start_date = end_date - timedelta(days=7)  # Last 7 days

stats = umami.website_stats(
    start_at=start_date,
    end_at=end_date,
    website_id='a7cd-5d1a-2b33'  # Only send if overriding default above
)
print(f"Page views: {stats.pageviews}")
print(f"Unique visitors: {stats.visitors}")
print(f"Bounce rate: {stats.bounces}")

# Get current active users count
active_count = umami.active_users(
    website_id='a7cd-5d1a-2b33'  # Only send if overriding default above
)
print(f"Currently active users: {active_count}")

# Check if Umami server is accessible
server_ok = umami.heartbeat()
print(f"Umami server is {'accessible' if server_ok else 'not accessible'}")

# Call after logging in to make sure the auth token is still valid.
umami.verify_token()
```

This code listing is very-very high fidelity psuedo code. If you want an actually executable example, see the [example client](./umami/example_client) in the repo.

## Want to contribute?

See the [API documentation](https://umami.is/docs/api) for the remaining endpoints to be added. PRs are welcome. But please open an issue first to see if the proposed feature fits with the direction of this library.

Enjoy.