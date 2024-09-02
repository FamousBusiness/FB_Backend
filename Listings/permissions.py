from rest_framework import permissions
from rest_framework_simplejwt.tokens import AccessToken
from users.models import User
from Listings.models import Business



class IsAdminuserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_staff
    


class IsAdminuserOrAllReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_staff
    



class CustomeTokenPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        access_token_cookie = request.COOKIES.get('access')

        if not access_token_cookie:
            return False
        try:
            acces_token = AccessToken(access_token_cookie)
        except:
            return False
        
        user_id = acces_token.payload.get('user')
      
        return bool(user_id and user_id.is_authenticated)
        # if access_token_cookie:
        #     return True
        # else:
        #     return False
    

        
        