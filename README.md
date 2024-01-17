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

umami.set_url_base("https://umami.hostedbyyouorthem.com")
login = umami.login(username, password)

# Skip the need to pass the target website in subsequent calls.
umami.set_website_id('cc726914-8e68-4d1a-4be0-af4ca8933456')
umami.set_hostname('somedomain.com')

# List your websites
websites = umami.websites()

# Create a new event in the events section of the dashboards.
event_resp = umami.new_event(
    website_id=sit'a7cd-5d1a-2b33', # Only send if overriding default above
    event_name='Umami-Test',
    title='Umami-Test', # Defaults to event_name if omitted.
    hostname='somedomain.com', # Only send if overriding default above.
    url='/users/actions',
    custom_data={'client': 'umami-tester-v1'},
    referrer='https://some_url')

# Call after logging in to make sure the auth token is still valid.
umami.verify_token()
```
