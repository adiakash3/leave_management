from channels.auth import AuthMiddlewareStack
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser


class TokenAuthMiddleware:
    """
    Token authorization middleware for Django Channels 2
    """

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        token = scope['query_string'].decode()
        if token:
            try:
                # token_name, token_key = headers[b'authorization'].decode().split()
                # token_name, token_key = headers[b'sec-websocket-protocol'].decode().split()
                token_key = token
                token = Token.objects.get(key=token_key)
                scope['user'] = token.user
            except Token.DoesNotExist:
                scope['user'] = AnonymousUser()
        return self.inner(scope)

TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))
