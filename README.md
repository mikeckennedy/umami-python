# Umami Analytics Client for Python

Analytics client for privacy-preserving, open source [Umami platform](https://umami.is) based on 
`httpx` and `pydantic`. 

## Partially implemented

Implemented endpoints:

* `POST /api/auth/login` as `login_async` and `login`
* `POST /api/auth/verify` as `verify_token_async` and `verify_token`
* `GET /api/websites` as `websites_async` and `websites`
* `POST /api/send` as `new_event_async` and `new_event`

See the [API documentation](https://umami.is/docs/api) for the remaining endpoints to be added (PRs welcome).

## Installation

Just `pip install umami-analytics`

## Usage

```python

import umami

umami.set_url_base(analytics_server_url)
login = umami.login(user, password)

# Skip the need to pass the target website in subseqent calls.
umami.set_website_id('cc726914-8e68-4d1a-4be0-af4ca8933456')

# List your websites
websites = umami.websites()

# Create a new event in the events section of the dashboards.
event_resp = umami.new_event(
    website_id=site.id,
    event_name='Umami-Test',
    title='Umami-Test',
    hostname='somedomain.com',
    url='/users/actions',
    custom_data={'client': 'umami-tester-v1'},
    referrer='https://some_url')
```
