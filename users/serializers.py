from rest_framework import serializers
from users.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from Listings.models import Business, BusinessImage
import time
from django.contrib.auth import authenticate
from .tasks import Utils
from django.contrib.auth import login




class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type':'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'mobile_number', 'business_name', 'location', 'password', 'password2']

    def validate(self, attrs):
        password = attrs['password']
        password2 = attrs['password2']

        if password != password2:
            raise serializers.ValidationError("Password and confirm Password did not match")
        return attrs
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    


class ClientRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type':'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'mobile_number', 'location', 'password', 'password2']

    def validate(self, attrs):
        password = attrs['password']
        password2 = attrs['password2']

        if password != password2:
            raise serializers.ValidationError("Password and confirm Password did not match")
        return attrs
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    

# class UserLoginSerializer(serializers.ModelSerializer):
#     # email = serializers.EmailField(max_length=255)
#     mobile_number = serializers.CharField(max_length=10)

#     class Meta:
#         model = User
#         fields = ['mobile_number', 'password']   


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    mobile_number = serializers.CharField(required=False, max_length=10)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        email         = data.get('email')
        mobile_number = data.get('mobile_number')
        password      = data.get('password')

        if not email and not mobile_number:
            raise serializers.ValidationError("Provide either email or mobile_number.")

        user = None

        if email:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            
        elif mobile_number:
            user = authenticate(request=self.context.get('request'), mobile_number=mobile_number, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid email/mobile_number or password.")
        
        login(self.context.get('request'), user)

        data['user'] = user
        return data
    

class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True) 
    password2 = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        user = self.context.get('user')

        if password != password2:
            raise serializers.ValidationError("Password and confirm password doesn/'t match")
        user.set_password(password)
        user.save()
        return attrs


class UserSendPasswordResetMailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():

            try:
                user = User.objects.get(email=email)
            except Exception as e:
                return serializers.ValidationError(f'Email ID does not exists')
            
            uid = urlsafe_base64_encode(force_bytes(user.id))
            # print(uid)
            token = PasswordResetTokenGenerator().make_token(user)
            # print(token)
            link = ' https://famousbusiness.in/login/forgot?uuid='+uid+'&token='+token
            # print(link)

            body = 'Click on the following link to Reset your password' + link
            data = {
                'subject': 'Reset Your Password',
                'body': body,
                'to_email': user.email
            }
            # print(data)
            Utils.send_mail_password_reset(data)

            return attrs
        else:
            return serializers.ValidationError('Not a Registered user')
        

class UserPasswordResetSerializer(serializers.Serializer):
    password  = serializers.CharField(max_length=245, style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(max_length=245, style={'input_type': 'password'}, write_only=True)

    def validate(self, attrs):
        try:
            password  = attrs.get('password')
            password2 = attrs.get('password2')
            uid       = self.context.get('uid')
            token     = self.context.get('token')

            if password != password2:
                raise serializers.ValidationError('Password did not match')
            
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError('Password Reset time out')
            
            user.set_password(password)
            user.save()
            return attrs
        
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError('Token is not valid or expired')
        

class UserSpecificBusinessPageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Business
        fields = ['business_name', 'business_info', 'category', 'website_url', 'city', 'state', 'pincode', 'address', 'employee_count',
                  'turn_over', 'nature', 'opening_time', 'closing_time', 'keywords', 'services', 'established_on', 'director', 'RoC',
                  'company_No', 'DIN', 'CIN_No', 'GSTIN', 'mobile_number', 'whatsapp_number']


class MailRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type':'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['name', 'password', 'password2']

    def validate(self, attrs):
        password = attrs['password']
        password2 = attrs['password2']
        uid = self.context.get('uid')
        token = self.context.get('token')

        if password != password2:
            raise serializers.ValidationError('Password Did not match')
        
        id             = smart_str(urlsafe_base64_decode(uid))
        business       = Business.objects.get(id=id)
        email          = business.email
        mobile_number  = business.mobile_number
        attrs['email'] = email
        attrs['mobile_number'] = mobile_number

        current_time = int(time.time())
        expiration_time = int(token)

        if current_time > expiration_time:
            raise serializers.ValidationError('Token has expired')
        
        return attrs
    
    def create(self, validated_data):
        email = validated_data.pop('email', None)
        mobile_number = validated_data.pop('mobile_number', None)

        user = User.objects.create(email=email, mobile_number=mobile_number,**validated_data)

        return user
    

class ClientRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type':'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['name', 'mobile_number', 'email','password', 'password2']

    def validate(self, attrs):
        password = attrs['password']
        password2 = attrs['password2']

        if password != password2:
            return serializers.ValidationError('Password did not match')
        return attrs
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data) 


    