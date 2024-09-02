from users.models import User



# class EmailAuthBackend(object):
#     def authenticate(self, request, mobile_number=None, password=None):
#         try:
#             user = User.objects.get(email=mobile_number)
#             if user.check_password(password):
#                 return user
#             return None
#         except User.DoesNotExist:
#             return None
#     def get_user(self, user_id):
#         try:
#             return User.objects.get(pk=user_id)
#         except User.DoesNotExist:
#             return None
        
class EmailAuthBackend(object):
    def authenticate(self, request, email=None, mobile_number=None, password=None):
        user = None

        if email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                pass

        if mobile_number and user is None:
            try:
                user = User.objects.get(mobile_number=mobile_number)
            except User.DoesNotExist:
                pass

        if user and user.check_password(password):
            return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
