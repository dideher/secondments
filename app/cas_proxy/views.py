import json
import logging

from django.shortcuts import resolve_url
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.views import RedirectURLMixin, REDIRECT_FIELD_NAME
from django.core.exceptions import PermissionDenied
from cas_proxy.signals import cas_proxy_user_logout
import urllib.parse
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
)
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from typing import Any
from django.conf import settings
import random
import string
from .utils import get_redirect_url, get_cas_proxy_login_url, get_random_string, get_request_url, \
    compute_secure_signature, get_cas_proxy_verify_ticket_url, get_cas_proxy_logout_url, clean_next_page
from .models import SESSION_KEY_MAXLENGTH, SessionTicket


class LogoutView(RedirectURLMixin, View):

    def successful_logout(self, request: HttpRequest, next_page: str) -> HttpResponse:
        """
        This method is called on successful logout. Override this method for
        custom post-auth actions (i.e, to add a cookie with a token).
        :param request:
        :param next_page:
        :return:
        """
        return HttpResponseRedirect(next_page)

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Redirects to CAS logout page
        :param request:
        :return:
        """

        next_page = clean_next_page(request, request.GET.get('next'))
        if not next_page:
            next_page = get_redirect_url(request)

        if request.user.is_authenticated is False:
            # user is not authenticated
            return self.successful_logout(request=request, next_page=next_page)

        # try to find the ticket matching current session for logout signal

        # Truncate session key to a max of its value length
        # When using the signed_cookies session backend, the
        # session key can potentially be longer than this.
        session_key = None
        if request.session and request.session.session_key:
            session_key = request.session.session_key[:SESSION_KEY_MAXLENGTH]

        try:
            st = SessionTicket.objects.get(session_key=session_key)
            ticket = st.ticket
        except SessionTicket.DoesNotExist:
            ticket = None

        # send logout signal
        cas_proxy_user_logout.send(
            sender="manual",
            user=request.user,
            session=request.session,
            ticket=ticket,
        )

        # clean current session ProxyGrantingTicket and SessionTicket
        SessionTicket.objects.filter(session_key=session_key).delete()
        auth_logout(request)

        if settings.CAS_PROXY_LOGOUT_COMPLETELY:

            url_params = {
                'u': get_request_url(request),
                't': ticket,
                'app': settings.CAS_PROXY_APP_NAME,
            }

            print("******* LogoutView : ")
            print(json.dumps(url_params, indent=2))

            cas_proxy_logout_url = get_cas_proxy_logout_url(request, url_params=url_params)
            return HttpResponseRedirect(cas_proxy_logout_url)

        # This is in most cases pointless if not CAS_RENEW is set. The user will
        # simply be logged in again on next request requiring authorization.
        return HttpResponseRedirect(next_page)


class LoginView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().dispatch(request, *args, **kwargs)

    def successful_login(self, request: HttpRequest, next_page: str) -> HttpResponse:
        """
        This method is called on successful login. Override this method for
        custom post-auth actions (i.e, to add a cookie with a token).
        :param request:
        :param next_page:
        :return:
        """
        return HttpResponseRedirect(next_page)

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Forwards to CAS login URL or verifies CAS ticket
        :param request:
        :return:
        """

        next_page = clean_next_page(request, request.GET.get('next'))
        required = request.GET.get('required', False)

        # if not next_page and settings.CAS_STORE_NEXT and 'CASNEXT' in request.session:
        #     next_page = request.session['CASNEXT']
        #     request.session['CASNEXT'] = None

        if not next_page:
            next_page = get_redirect_url(request)

        print("******* next_page : ", next_page)

        if request.user.is_authenticated:
            # user is already authenticated

            return self.successful_login(request=request, next_page=next_page)

        ticket = request.GET.get('ticket')

        if not ticket:

            if settings.CAS_PROXY_STORE_NEXT:
                request.session['CAS_PROXY_NEXT'] = next_page

            digest = compute_secure_signature()
            digest_str = digest.hexdigest()

            url_params = {
                'd': digest_str,
                'u': get_request_url(request)
            }

            print("******* LoginView : ")
            print(json.dumps(url_params, indent=2))

            redirect_url = get_cas_proxy_login_url(request, url_params=url_params)

            return HttpResponseRedirect(redirect_url)

        # if we are here, we have received the callback from the CAS_PROXY, so
        # go ahead and verify the ticket

        user = authenticate(request=request,
                            ticket=ticket,
                            cas_proxy_url=get_cas_proxy_verify_ticket_url(request))

        if user is not None:
            auth_login(request, user)

            # from https://code.djangoproject.com/ticket/19147
            if not request.session.session_key:
                request.session.save()

            # Truncate session key to a max of its value length.
            # When using the signed_cookies session backend, the
            # session key can potentially be longer than this.
            session_key = request.session.session_key[:SESSION_KEY_MAXLENGTH]

            if not request.session.exists(session_key):
                request.session.create()

            try:
                st: SessionTicket = SessionTicket.objects.get(session_key=session_key)
                st.ticket = ticket
                st.logged_in = timezone.now()
                st.save()
            except SessionTicket.DoesNotExist:
                SessionTicket.create(
                    session_key=session_key,
                    ticket=ticket,
                )

            return self.successful_login(request=request, next_page=next_page)

        # could not authenticate
        if settings.CAS_PROXY_RETRY_LOGIN or required:
            digest = compute_secure_signature()
            digest_str = digest.hexdigest()

            url_params = {
                'd': digest_str,
                'u': get_request_url(request)
            }

            redirect_url = get_cas_proxy_login_url(request, url_params=url_params)

            return HttpResponseRedirect(redirect_url)

        raise PermissionDenied(_('Login failed.'))

