from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.http.request import HttpRequest


class CustomAuthentication(ModelBackend):
    def authenticate(self, request: HttpRequest, username=None, password=None, **kwargs):
        UserModel = get_user_model()

        # try:
        #     user = UserModel.objects.get(email=username)
        # except UserModel.DoesNotExist:
        # try:
        #     user = UserModel.objects.get(mobile_number=username)
        # except UserModel.DoesNotExist:
        #     try:
        #         user = UserModel.objects.get(name=username)
        #     except UserModel.DoesNotExist:
        #         return None
                
        # if user.check_password(password):
        #     return user
        # else:
        #     return None
        