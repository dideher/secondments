import django.utils.timezone
from importlib import import_module
from django.db import models
from django.conf import settings
from .utils import get_user_from_session

SESSION_KEY_MAXLENGTH = 1024


SessionStore = import_module(settings.SESSION_ENGINE).SessionStore


class SessionTicket(models.Model):
    session_key = models.CharField(max_length=SESSION_KEY_MAXLENGTH)
    ticket = models.CharField(max_length=1024, null=False, blank=False)
    created_on = models.DateTimeField(null=False, blank=False, default=django.utils.timezone.now)
    logged_in = models.DateTimeField(null=False, blank=False, default=django.utils.timezone.now)

    @classmethod
    def create(cls, session_key: str, ticket: str):
        return cls.objects.create(
                    session_key=session_key,
                    ticket=ticket,
                )

    @classmethod
    def clean_deleted_sessions(cls) -> None:
        for st in cls.objects.all():
            session = SessionStore(session_key=st.session_key)
            user = get_user_from_session(session)
            if not user.is_authenticated:
                st.delete()