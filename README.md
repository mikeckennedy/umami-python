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

websites = umami.websites()

site = [w for w in websites if w.domain == site_domain][0]

event_resp = umami.new_event(
    website_id=site.id,
    event_name='Umami-Test',
    title='Umami-Test',
    hostname=site.domain,
    url='/users/actions',
    custom_data={'client': 'umami-tester-v1'},
    referrer='https://some_url')
```
