from rest_framework import serializers
from Admin.social_register import register_social_user
from users.models import User, UsersAgreement
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from Listings.models import Business
from . import google
from rest_framework.exceptions import AuthenticationFailed
from decouple import config





class UserPasswordResetAfterMailSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=245, style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(max_length=245, style={'input_type': 'password'}, write_only=True)

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            password2 = attrs.get('password2')
            uid = self.context.get('uid')
            # token = self.context.get('token')

            if password != password2:
                raise serializers.ValidationError('Password did not match')
            name = smart_str(urlsafe_base64_decode(uid))

            try:
                business_page = Business.objects.get(business_name=name)
            except Business.DoesNotExist:
                serializers.ValidationError('Business page Does Not Exist')
            
            try:
                user = User.objects.get(name=business_page.owner)
            except User.DoesNotExist:
                serializers.ValidationError('User does not Exists')

            # if not PasswordResetTokenGenerator().check_token(user, token):
            #     raise serializers.ValidationError('Password Reset time out')
            
            user.set_password(password)
            user.save()
            UsersAgreement.objects.create(user=user, termsandconditions=True)
            return attrs
        except DjangoUnicodeDecodeError as identifier:
            # PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError('Token is not valid or expired')
        



# class GoogleSocialAuthSerializer(serializers.Serializer):
#     auth_token = serializers.CharField()

#     def validate_auth_token(self, auth_token):
#         user_data = google.Google.validate(auth_token)

#         try:
#             user_data['sub']
#         except:
#             raise serializers.ValidationError(
#                 'The token is invalid or expired. Please login again.'
#             )

#         if user_data['aud'] != config('GOOGLE_CLIENT_ID'):

#             raise AuthenticationFailed('oops, who are you?')

#         user_id = user_data['sub']
#         email = user_data['email']
#         name = user_data['name']
#         provider = 'google'

#         return register_social_user(
#             provider=provider, user_id=user_id, email=email, name=name)
