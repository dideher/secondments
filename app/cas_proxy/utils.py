import warnings
import random
import string
import urllib.parse
import hmac
import hashlib
import base64
from typing import Optional, Union
from urllib import parse as urllib_parse

from django.conf import settings as django_settings
from django.contrib.auth import (
    BACKEND_SESSION_KEY,
    REDIRECT_FIELD_NAME,
    SESSION_KEY,
    load_backend,
)
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.backends.base import SessionBase
from django.http import HttpRequest
from django.shortcuts import resolve_url


class RedirectException(Exception):
    """Signals that a redirect could not be handled."""
    pass


def get_protocol(request: HttpRequest) -> str:
    """Returns 'http' or 'https' for the request protocol"""
    if request.is_secure():
        return 'https'
    return 'http'


def get_random_string(length):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))


def compute_secure_signature() -> hmac.HMAC:
    message = django_settings.CAS_PROXY_APP_NAME + get_random_string(12)
    secret_key_bytes = bytes(django_settings.CAS_PROXY_SECRET_KEY, 'utf-8')
    msg_bytes = bytes(message, 'utf-8')

    return hmac.new(key=secret_key_bytes, msg=msg_bytes, digestmod=hashlib.sha256)


def get_cas_proxy_login_url(request: HttpRequest, url_params):

    login_url = f'{django_settings.CAS_PROXY_URL}/login/{django_settings.CAS_PROXY_APP_NAME}?{urllib.parse.urlencode(url_params)}'
    return login_url


def get_cas_proxy_logout_url(request: HttpRequest, url_params):

    logout_url = f'{django_settings.CAS_PROXY_URL}/logout?{urllib.parse.urlencode(url_params)}'
    return logout_url

def get_cas_proxy_verify_ticket_url(request: HttpRequest, url_params=None):
    verify_ticket_url = f'{django_settings.CAS_PROXY_URL}/login/{django_settings.CAS_PROXY_APP_NAME}/verify'

    if url_params is not None:
        verify_ticket_url = verify_ticket_url + f'?{urllib.parse.urlencode(url_params)}'

    return verify_ticket_url


def get_request_url(request: HttpRequest) -> str:
    server_host = request.get_host()
    server_port = request.get_port()

    if server_port not in ["80", "443"]:
        host = f'{server_host}:{server_port}'
    else:
        host = server_host

    return urllib_parse.urlunparse(
        (get_protocol(request), host, request.get_full_path(), '', '', ''),
    )


def get_redirect_url(request: HttpRequest) -> str:
    """Redirects to referring page, or CAS_PROXY_REDIRECT_URL if no referrer is
    set.
    """

    next_ = request.GET.get(REDIRECT_FIELD_NAME)
    if not next_:
        redirect_url = resolve_url(django_settings.CAS_PROXY_REDIRECT_URL)
        if django_settings.CAS_PROXY_IGNORE_REFERER:
            next_ = redirect_url
        else:
            next_ = request.META.get('HTTP_REFERER', redirect_url)
        prefix = urllib_parse.urlunparse(
            (get_protocol(request), request.get_host(), '', '', '', ''),
        )
        if next_.startswith(prefix):
            next_ = next_[len(prefix):]
    return next_


def get_user_from_session(session: SessionBase) -> Union[User, AnonymousUser]:
    """
    Get User object (or AnonymousUser() if not logged in) from session.
    """
    try:
        user_id = session[SESSION_KEY]
        backend_path = session[BACKEND_SESSION_KEY]
        backend = load_backend(backend_path)
        return backend.get_user(user_id) or AnonymousUser()
    except KeyError:
        return AnonymousUser()


def is_local_url(host_url, url):
    """
    :param host_url: is an absolute host url, say https://site.com/
    :param url: is any url
    :return: Is :url: local to :host_url:?
    """
    url = url.strip()
    parsed_url = urllib_parse.urlparse(url)
    if not parsed_url.netloc:
        return True
    parsed_host = urllib_parse.urlparse(host_url)
    if parsed_url.netloc != parsed_host.netloc:
        return False
    if parsed_url.scheme != parsed_host.scheme and parsed_url.scheme:
        return False
    url_path = parsed_url.path if parsed_url.path.endswith('/') else parsed_url.path + '/'
    host_path = parsed_host.path if parsed_host.path.endswith('/') else parsed_host.path + '/'
    return url_path.startswith(host_path)


def clean_next_page(request, next_page):
    if not next_page:
        return next_page
    if django_settings.CAS_PROXY_CHECK_NEXT and not is_local_url(request.build_absolute_uri('/'), next_page):
        raise RedirectException("Non-local url is forbidden to be redirected to.")
    return next_page

