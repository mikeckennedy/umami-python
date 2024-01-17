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
