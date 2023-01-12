
from typing import Mapping, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User, Group
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest
from cas_proxy.utils import compute_secure_signature
from cas_proxy.signals import cas_proxy_user_authenticated
import requests

__all__ = ['CASProxyBackend']


def verify_cas_proxy_ticket(cas_proxy_url: str, ticket:str):

    p = {
        'd': compute_secure_signature().hexdigest(),
        't': ticket,
    }
    r = requests.get(cas_proxy_url, params=p)
    if r.status_code == 200:
        return r.json()
    else:
        return None


class CASProxyBackend(ModelBackend):

    def authenticate(self, request: HttpRequest, ticket: str, cas_proxy_url: str) -> Optional[User]:

        # contact cas_proxy to verify
        print("authenticate: ticket -> %s" % ticket)
        print("authenticate: cas_proxy_url -> %s" % cas_proxy_url)
        verify_object = verify_cas_proxy_ticket(cas_proxy_url, ticket)
        print(verify_object)

        if verify_object is None:
            return None

        cas_user = verify_object.get('u')
        cas_attributes = verify_object.get('a')

        if not cas_user:
            return None

        cas_user = self.clean_username(cas_user)

        if cas_attributes is not None:
            for cas_attr_name, req_attr_name in settings.CAS_PROXY_RENAME_ATTRIBUTES.items():
                if cas_attr_name in cas_attributes and cas_attr_name is not req_attr_name:
                    cas_attributes[req_attr_name] = cas_attributes[cas_attr_name]
                    cas_attributes.pop(cas_attr_name)

        UserModel = get_user_model()
        user = None
        if settings.CAS_PROXY_CREATE_USER:
            user_kwargs = {
                UserModel.USERNAME_FIELD: cas_user
            }
            if settings.CAS_PROXY_CREATE_USER_WITH_ID:
                user_kwargs['id'] = self.get_user_id(cas_attributes)

            user, created = UserModel._default_manager.get_or_create(**user_kwargs)
            if created:
                user = self.configure_user(user)
        else:
            try:
                if settings.CAS_PROXY_LOCAL_NAME_FIELD:
                    user_kwargs = {
                        settings.CAS_PROXY_LOCAL_NAME_FIELD: cas_user

                    }
                    user = UserModel._default_manager.get(**user_kwargs)
                else:
                    user = UserModel._default_manager.get_by_natural_key(cas_user)
            except UserModel.DoesNotExist:
                pass

        if not self.user_can_authenticate(user):
            return None

        if settings.CAS_PROXY_APPLY_ATTRIBUTES_TO_USER and cas_attributes:
            # If we are receiving None for any values which cannot be NULL
            # in the User model, set them to an empty string instead.
            # Possibly it would be desirable to let these throw an error
            # and push the responsibility to the CAS provider or remove
            # them from the dictionary entirely instead. Handling these
            # is a little ambiguous.
            user_model_fields = UserModel._meta.fields
            for field in user_model_fields:
                # Handle null -> '' conversions mentioned above
                if not field.null:
                    try:
                        if cas_attributes[field.name] is None:
                            cas_attributes[field.name] = ''
                    except KeyError:
                        continue
                # Coerce boolean strings into true booleans
                if field.get_internal_type() == 'BooleanField':
                    try:
                        boolean_value = cas_attributes[field.name] == 'True'
                        cas_attributes[field.name] = boolean_value
                    except KeyError:
                        continue

            user.__dict__.update(cas_attributes)

            # If we are keeping a local copy of the user model we
            # should save these attributes which have a corresponding
            # instance in the DB.
            if settings.CAS_PROXY_CREATE_USER:
                user.save()

        # send the `cas_user_authenticated` signal
        cas_proxy_user_authenticated.send(
            sender=self,
            user=user,
            created=created,
            username=cas_user,
            attributes=cas_attributes,
            pgtiou=None,
            ticket=ticket,
            service=None,
            request=request
        )
        return user

    def clean_username(self, username: str) -> str:
        """
        Performs any cleaning on the ``username`` prior to using it to get or
        create the user object.
        By default, changes the username case according to
        `settings.CAS_FORCE_CHANGE_USERNAME_CASE`.
        :param username: [string] username.
        :returns: [string] The cleaned username.
        """
        username_case = settings.CAS_PROXY_FORCE_CHANGE_USERNAME_CASE
        if username_case == 'lower':
            username = username.lower()
        elif username_case == 'upper':
            username = username.upper()
        elif username_case is not None:
            raise ImproperlyConfigured(
                "Invalid value for the CAS_PROXY_FORCE_CHANGE_USERNAME_CASE setting. "
                "Valid values are `'lower'`, `'upper'`, and `None`.")
        return username

    def get_user_id(self, attributes: Mapping[str, str]) -> str:
        """
        For use when CAS_PROXY_CREATE_USER_WITH_ID is True. Will raise ImproperlyConfigured
        exceptions when a user_id cannot be accessed. This is important because we
        shouldn't create Users with automatically assigned ids if we are trying to
        keep User primary key's in sync.
        :returns: [string] user id.
        """
        if not attributes:
            raise ImproperlyConfigured("CAS_PROXY_CREATE_USER_WITH_ID is True, but "
                                       "no attributes were provided")

        user_id = attributes.get('id')

        if not user_id:
            raise ImproperlyConfigured("CAS_PROXY_CREATE_USER_WITH_ID is True, but "
                                       "`'id'` is not part of attributes.")

        return user_id

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        return getattr(user, "is_active", True)

    def configure_user(self, user: User) -> User:
        """
        Configures a user after creation and returns the updated user.
        This method is called immediately after a new user is created,
        and can be used to perform custom setup actions.
        :param user: User object.
        :returns: [User] The user object. By default, returns the user unmodified.
        """
        return user

