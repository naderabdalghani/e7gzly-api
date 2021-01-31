from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from .models import Token


class TokenAuthentication(BaseAuthentication):
    keyword = 'Bearer'

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            raise AuthenticationFailed('Invalid token header. No credentials provided')
        elif len(auth) > 2:
            raise AuthenticationFailed('Invalid token header. Token string should not contain spaces')

        try:
            key = auth[1].decode()
        except UnicodeError:
            raise AuthenticationFailed('Invalid token header. Token string should not contain invalid characters')

        try:
            token = Token.nodes.get(key=key)
        except Token.DoesNotExist:
            raise AuthenticationFailed('Invalid token')

        if token.user.single() is None:
            raise AuthenticationFailed("User doesn't exist/deleted")

        return token.user.single(), token

    def authenticate_header(self, request):
        return self.keyword
