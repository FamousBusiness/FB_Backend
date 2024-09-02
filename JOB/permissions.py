from rest_framework import permissions


class CustomeTokenPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        access_token_cookie = request.COOKIES.get('access')

        if access_token_cookie:
            return True
        else:
            return False