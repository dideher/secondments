from django.conf import settings
from django.utils.translation import gettext_lazy as _

__all__ = []

# Where to send a user after logging in or out if there is no referrer and no next page set.
CAS_PROXY_REDIRECT_URL = '/'

# If True and an unknown or invalid ticket is received, the user is redirected back to the
# login page.
CAS_PROXY_RETRY_LOGIN = False

# If `True`, logging out of the application will always send the user to the URL specified by CAS_PROXY_REDIRECT_URL.
CAS_PROXY_IGNORE_REFERER = True

# If True, the page to redirect to following login will be stored as a session variable, which can avoid encoding
# errors depending on the CAS implementation.
CAS_PROXY_STORE_NEXT = False

# Create a user when the CAS authentication is successful.
CAS_PROXY_CREATE_USER = True

# Create a user using the id field provided by the attributes returned by the CAS provider. Raises
# ImproperlyConfigured exception if attributes are not provided or do not contain the field id.
CAS_PROXY_CREATE_USER_WITH_ID = False


# If lower, usernames returned from CAS are lowercased before we check whether their
# account already exists. Allows user Joe to log in to CAS either as joe or JOE without
# duplicate accounts being created by Django (since Django allows case-sensitive duplicates).
# If upper, the submitted username will be uppercased.
CAS_PROXY_FORCE_CHANGE_USERNAME_CASE = 'lower'

# If True any attributes returned by the CAS provider included in the ticket will be applied
# to the User model returned by authentication. This is useful if your provider is
# including details about the User which should be reflected in your model.
CAS_PROXY_APPLY_ATTRIBUTES_TO_USER = True

# A dict used to rename the (key of the) attributes that the CAS server may retrun. For example, if
# CAS_PROXY_RENAME_ATTRIBUTES = {'ln':'last_name'} the ln attribute returned by the cas server will be renamed as
# last_name. Used with CAS_PROXY_APPLY_ATTRIBUTES_TO_USER = True, this provides an easy way to fill in Django
# Users’ info independently from the attributes’ keys returned by the CAS server.
CAS_PROXY_RENAME_ATTRIBUTES = {}

# If set, will make user lookup against this field and not model’s natural key. This allows you to authenticate
# arbitrary users.
CAS_PROXY_LOCAL_NAME_FIELD = None

# If False, logging out of the application won’t log the user out of CAS as well.
CAS_PROXY_LOGOUT_COMPLETELY = True

# The URL provided by ?next is validated so that only local URLs are allowed. This check can be disabled by turning
# this setting to False (e.g. for local development).
CAS_PROXY_CHECK_NEXT = True

_DEFAULTS = {
    'CAS_PROXY_REDIRECT_URL': CAS_PROXY_REDIRECT_URL,
    'CAS_PROXY_RETRY_LOGIN': CAS_PROXY_RETRY_LOGIN,
    'CAS_PROXY_IGNORE_REFERER': CAS_PROXY_IGNORE_REFERER,
    'CAS_PROXY_STORE_NEXT': CAS_PROXY_STORE_NEXT,
    'CAS_PROXY_CREATE_USER': CAS_PROXY_CREATE_USER,
    'CAS_PROXY_CREATE_USER_WITH_ID': CAS_PROXY_CREATE_USER_WITH_ID,
    'CAS_PROXY_FORCE_CHANGE_USERNAME_CASE': CAS_PROXY_FORCE_CHANGE_USERNAME_CASE,
    'CAS_PROXY_APPLY_ATTRIBUTES_TO_USER': CAS_PROXY_APPLY_ATTRIBUTES_TO_USER,
    'CAS_PROXY_RENAME_ATTRIBUTES': CAS_PROXY_RENAME_ATTRIBUTES,
    'CAS_PROXY_LOCAL_NAME_FIELD': CAS_PROXY_LOCAL_NAME_FIELD,
    'CAS_PROXY_LOGOUT_COMPLETELY': CAS_PROXY_LOGOUT_COMPLETELY,
    'CAS_PROXY_CHECK_NEXT': CAS_PROXY_CHECK_NEXT,
}

for key, value in list(_DEFAULTS.items()):
    try:
        getattr(settings, key)
    except AttributeError:
        setattr(settings, key, value)
    # Suppress errors from DJANGO_SETTINGS_MODULE not being set
    except ImportError:
        pass
