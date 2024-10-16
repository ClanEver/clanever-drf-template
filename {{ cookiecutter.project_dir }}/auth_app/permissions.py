from functools import wraps

from django.http import HttpResponse
from rest_framework import permissions


class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser


def user_is_superuser(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponse(b'401 Unauthorized', status=401)
        if not request.user.is_superuser:
            return HttpResponse(b'403 Permission Denied', status=403)
        return view_func(request, *args, **kwargs)

    return _wrapped_view
