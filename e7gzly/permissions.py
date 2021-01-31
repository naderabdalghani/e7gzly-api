from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import BasePermission, SAFE_METHODS

from e7gzly.models import User


class IsReadOnlyRequest(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsPostRequest(BasePermission):
    def has_permission(self, request, view):
        return request.method == "POST"


class IsPutRequest(BasePermission):
    def has_permission(self, request, view):
        return request.method == "PUT"


class IsPatchRequest(BasePermission):
    def has_permission(self, request, view):
        return request.method == "PATCH"


class IsDeleteRequest(BasePermission):
    def has_permission(self, request, view):
        return request.method == "DELETE"


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if type(request.user) is not User:
            raise NotAuthenticated
        return request.user.role == "admin"


class IsManager(BasePermission):
    def has_permission(self, request, view):
        if type(request.user) is not User:
            raise NotAuthenticated
        return request.user.role == "manager"


class IsFan(BasePermission):
    def has_permission(self, request, view):
        if type(request.user) is not User:
            raise NotAuthenticated
        return request.user.role == "fan"


class IsUser(BasePermission):
    def has_permission(self, request, view):
        if type(request.user) is not User:
            raise NotAuthenticated
        return True


class IsAuthorized(BasePermission):
    def has_permission(self, request, view):
        if type(request.user) is not User:
            raise NotAuthenticated
        return bool(request.user.authorized)
