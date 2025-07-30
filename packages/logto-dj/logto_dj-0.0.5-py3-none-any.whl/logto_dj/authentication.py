import json
from urllib.request import urlopen

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from jose import jwt
from rest_framework import authentication, exceptions


class LogtoAuthentication(authentication.BaseAuthentication):
    def get_user_from_payload(self, payload):
        """
        Load a Django user from the JWT payload.

        By default, returns AnonymousUser. Override this method in subclasses
        to implement custom user loading logic based on the token payload.

        Args:
            payload (dict): The decoded JWT payload

        Returns:
            User: A Django user instance (AnonymousUser by default)
        """
        return AnonymousUser()

    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).decode("utf-8")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise exceptions.AuthenticationFailed("No credentials provided or invalid token format.")
        token = auth_header.split(" ")[1]

        jwks_uri = urlopen(f"{settings.LOGTO_ENDPOINT}/oidc/jwks")
        jwks = json.loads(jwks_uri.read())
        issuer = f"{settings.LOGTO_ENDPOINT}/oidc"

        try:
            payload = jwt.decode(
                token,
                jwks,
                algorithms=jwt.get_unverified_header(token).get('alg'),
                audience='http://localhost:8000',
                issuer=issuer,
                options={
                    'verify_at_hash': False
                },
            )

            user = self.get_user_from_payload(payload)
            return user, token
        except Exception as e:
            # exception handler
            raise exceptions.AuthenticationFailed(f"Invalid token: {str(e)}")
