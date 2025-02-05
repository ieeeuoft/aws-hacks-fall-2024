# API
This app is largely a wrapper to coordinate the API endpoints for the various other apps.

Generally speaking, each app will implement it's own serializers, views, and URL routes for the API. Views may be in `views.py`, or a dedicated `api_views.py` to differentiate them from regular user-facing views. API url routes should be put in a standard url config file named `api_urls.py`. These are included by `api.urls` with the appropriate namespaces, which itself is included in the base urlconf `hackathon_site.urls` with the `api` namespace.

## Authentication
Two authentication schemes are enabled by default: [Token Authentication](https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication) and [Session Authentication](https://www.django-rest-framework.org/api-guide/authentication/#sessionauthentication), in that order.

The API tests and frontend are implemented assuming that non-authenticated requests will return a status `HTTP 401 Unauthorized`. This [requires](https://tools.ietf.org/html/rfc7235#section-3.1) that a `WWW-Authenticate` header be set in the response. Django Rest Framework's Session Authentication does not implement this header, and so it's status code for unauthenticated requests will be `HTTP 403 Permission Denied`. The type of response DRF uses is [determined by the first authentication class on the view](https://www.django-rest-framework.org/api-guide/authentication/#unauthorized-and-forbidden-responses). For this reason, the first provided default authentication class in [the settings file](/hackathon_site/settings/__init__.py) is Token Authentication, so DRF will return a `HTTP 401 Unauthorized` with the `WWW-Authenticate: Token` header, regardless of whether the view was authenticated with the Token on Session authentication classes.

You may change these authentication classes however you like, as long as the first one in the list includes the `WWW-Authenticate` header for unauthenticated responses (for example, [JWT](https://github.com/SimpleJWT/django-rest-framework-simplejwt) or [OAuth](https://github.com/jazzband/django-oauth-toolkit)).
