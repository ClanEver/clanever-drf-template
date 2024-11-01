from admin_ext.models import AuthToken


def create_knox_token(token_model, user, serializer):  # noqa
    return AuthToken.objects.create(user=user)
