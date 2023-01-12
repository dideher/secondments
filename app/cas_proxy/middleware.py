from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.views import LoginView as login, LogoutView as logout
from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from cas_proxy.views import LoginView as cas_proxy_login, LogoutView as cas_proxy_logout


class CASProxyMiddleware(MiddlewareMixin):

    def process_request(self, request: HttpRequest):
        """Checks that the authentication middleware is installed"""

        error = ("The Django CAS middleware requires authentication "
                 "middleware to be installed. Edit your MIDDLEWARE_CLASSES "
                 "setting to insert 'django.contrib.auth.middleware."
                 "AuthenticationMiddleware'.")
        if not hasattr(request, 'user'):
            raise ImproperlyConfigured(error)

    def process_view(self, request, view_func, view_args, view_kwargs):
        """Forwards unauthenticated requests to the admin page to the CAS
        login URL, as well as calls to django.contrib.auth.views.login and
        logout.
        """

        print(view_func.__module__)

        if view_func == login:
            return cas_proxy_login(request, *view_args, **view_kwargs)

        if view_func == logout:
            return cas_proxy_logout(request, *view_args, **view_kwargs)

        if view_func in (cas_proxy_login, cas_proxy_logout):
            return None

        # need to update this
        if True:#settings.CAS_ADMIN_REDIRECT:
            if not view_func.__module__.startswith('django.contrib.admin.'):
                return None

        if request.user.is_authenticated:
            if request.user.is_staff:
                return None
