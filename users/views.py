import random
from django.contrib.auth import authenticate, logout
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.utils.encoding import smart_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from Listings.ADS.ads_serializers import AdSerializer
from ADS.models import ADS
from Listings.models import Business, Assigned_Benefits, Category
from Brands.models import BrandBusinessPage
from Listings.serializers import BusinessSerializer
from users.models import User, UsersAgreement
from users.serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserChangePasswordSerializer,
    UserSendPasswordResetMailSerializer, UserPasswordResetSerializer, UserSpecificBusinessPageSerializer,
    MailRegisterSerializer, ClientRegisterSerializer
)
from PremiumPlan.models import PremiumPlanBenefits
from Admin.tasks import send_email
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
# from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
# from django.middleware.csrf import get_token
from django.http import HttpResponse





def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def home_view(request):
    return render(request, 'home.html')
  


#Business Page Registration
class UserRegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)

        GST            = request.data.get('GSTIN')
        CIN_No         = request.data.get('CIN_No')
        business_info  = request.data.get('business_info')
        category       = request.data.get('category')
        website_url    = request.data.get('website_url')
        city           = request.data.get('city')
        state          = request.data.get('state')
        pincode        = request.data.get('pincode')
        address        = request.data.get('address')
        employee_count = request.data.get('employee_count')
        turn_over      = request.data.get('turn_over')
        nature         = request.data.get('nature')
        opening_time   = request.data.get('opening_time')
        closing_time   = request.data.get('closing_time')
        keywords       = request.data.get('keywords')
        services       = request.data.get('services')
        established_on = request.data.get('established_on')
        director       = request.data.get('director')
        RoC            = request.data.get('RoC')
        company_No     = request.data.get('company_No')
        DIN            = request.data.get('DIN')
        whatsapp_number= request.data.get('whatsapp_number')
        
        
        if serializer.is_valid(raise_exception=True):
            mobile_number = serializer.validated_data.get('mobile_number')
            to_email      = serializer.validated_data.get('email')
            business_name = serializer.validated_data.get('business_name')
            # send_otp_via_message.delay(mobile_number, otp)
            # send_mail_to_business.delay(to_email)
            
            user = serializer.save()

            try:
                category_id = Category.objects.get(pk=category)
            except:
                category_id = None

            try:
                business = Business.objects.create(
                    owner=user, 
                    business_name=business_name, 
                    mobile_number=mobile_number, 
                    email=to_email,
                    state=state, 
                    city=city, 
                    pincode=pincode,
                    address=address,
                    website_url=website_url, 
                    director=director, 
                    business_info=business_info,
                    established_on=established_on, 
                    services=services, 
                    keywords=keywords, 
                    opening_time=opening_time,
                    closing_time=closing_time, 
                    nature=nature, 
                    turn_over=turn_over, 
                    employee_count=employee_count,
                    category = category_id if category_id else None
                    )
                if GST:
                    business.GSTIN=GST
                if CIN_No:
                    business.CIN_No = CIN_No
                if DIN:
                    business.DIN = DIN
                if RoC:
                    business.RoC = RoC
                if whatsapp_number:
                    business.whatsapp_number = whatsapp_number
                if company_No:
                    business.company_No = company_No

                uid   = urlsafe_base64_encode(force_bytes(business.business_name))

                link = f'https://famousbusiness.in/userprofile/{business.business_name}?z_id={business.pk}&mail=mail&uuid={uid}'

                data = [ 
                            {
                            'subject': 'Elevate Your Business with Exclusive PAN India Leads',
                            'to_email': business.email,
                            'link': link,
                            'business_name': business.business_name
                            }
                        ]

                send_email.delay(data)
                
            except Exception as e:
                return Response({'msg': f'Business Page did not get crerated {str(e)}'})
            
            UsersAgreement.objects.create(user=user, termsandconditions=True)

            return Response({'msg': 'Registered Succefully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'msg': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)
        


#Client Registration(Whoes donot have a business Page)
class ClientRegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ClientRegisterSerializer(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            mobile_number = serializer.validated_data.get('mobile_number')
            to_email = serializer.validated_data.get('email')

            user = serializer.save()
            UsersAgreement.objects.create(user=user, termsandconditions=True)

            respone  = Response({'msg': 'Registered Succefully'}, status=status.HTTP_201_CREATED)
            return respone
        else:
            return Response({'msg': 'Invalid Credentials'}, status=status.HTTP_404_NOT_FOUND)




# class LoginAuthAPIView(APIView):
#     # renderer_classes = [UserRenderer]
#     permission_classes = [permissions.AllowAny,]

#     def post(self, request):
#         serializer  = UserLoginSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         # email = serializer.validated_data.get('email')
#         mobile_number = serializer.validated_data.get('mobile_number')
#         password = serializer.validated_data.get('password')

#         # user = authenticate(email=email, password=password)
#         otp = random.randint(10000, 99999)
#         user = authenticate(mobile_number=mobile_number, password=password)

#         if user is not None:
#             user_name = user.name
#             token = get_tokens_for_user(user)
#             try:
#                 business = Business.objects.get(owner=user)
#                 return Response({'token': token, 'msg': "Login Success", 'user_name': user_name,
#                                  'business_id': business.id }, status=status.HTTP_200_OK)
#             except Business.DoesNotExist:
#                 return Response({'token': token, 'msg': "Login Success", 'user_name': user_name}, status=status.HTTP_200_OK)
#         else:
#             return Response({'errors':{'non_field_errors':['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)



class LoginAuthAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data.get('user')
        token = get_tokens_for_user(user)

        try:
            business = Business.objects.get(owner=user)

            #If Business owner has purshased any premium plan
            try:
                premium_plans = PremiumPlanBenefits.objects.filter(user=user)
                plan_status   = any(plan.expired for plan in premium_plans)

                response = Response({
                    'token': token,
                    'msg': "You are successfully logged in", 
                    'user_name': user.name, 'business_id': business.pk, 
                    'mobile_number': user.mobile_number, 
                    'plan_status': plan_status}, status=status.HTTP_200_OK)
                
            except PremiumPlanBenefits.DoesNotExist:
                response = Response({
                                    'token': token,
                                     'msg': "You are successfully logged in", 
                                     'user_name': user.name, 
                                     'business_id': business.id, 
                                     'mobile_number': user.mobile_number 
                             }, status=status.HTTP_200_OK)
            
            return response
        except Business.DoesNotExist:
            try:
                brand = BrandBusinessPage.objects.get(owner=user)
                response = Response({ 
                                    'token': token,
                                     'msg': "You are successfully logged in", 
                                     'user_name': user.name, 
                                     'brand_id': brand.id, 
                                     'mobile_number': user.mobile_number }, status=status.HTTP_200_OK)
                return response
            except:
                response =  Response({
                                      'token': token,
                                      'msg': "Login Success", 
                                      'user_name': user.name,
                                       'mobile_number': user.mobile_number}, status=status.HTTP_200_OK)
                return response
            
        


class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            print(refresh_token)
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            logout(request)
            return Response({'msg': 'Logged out successfully'},status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)



#Replace num_views with the received from frontend
#Not used anywhere
class UserBusinessPageAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def put(self, request, business_id):
        try:
            business = Business.objects.get(id=business_id)
        except Business.DoesNotExist:
            return Response({'msg': 'Business Not Listed'}, status=status.HTTP_404_NOT_FOUND)
        
        if business.owner != request.user:
            return Response({'msg': 'You are not page owner'}, status=status.HTTP_403_FORBIDDEN)
        
        # try:
        #     user_premium_plan = UserPremiumPlan.objects.get(user=request.user)
        # except UserPremiumPlan.DoesNotExist:
        #     return Response({'msg': 'Please Recharge'})
        
        # if not user_premium_plan.is_active == True:
        #     return Response({'mag': 'Donot have any active plan'})
        
        serializer = UserSpecificBusinessPageSerializer(business, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'Updated Successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   
    
    def get(self, request):
            user = request.user
            business = get_object_or_404(Business, owner=user)
            category = business.category
            ads = ADS.objects.filter(category=category)
            business_serializer = BusinessSerializer(business)

            user_assigned_benefits = Assigned_Benefits.objects.filter(user=user)

            num_views = user_assigned_benefits.aggregate(num_views=Count('ads_views'))['num_views']

            all_users = User.objects.filter(business__category=category)

            if num_views > len(all_users):
                num_views = len(all_users) - 1

            random_users = random.sample(list(all_users), num_views)

            verified_ads = []
            ads_not_approved = False
            ads_expired = False

            for ad in ads:
                if ad.posted_by in random_users and ad.verified and not ad.expired:
                    verified_ads.append(ad)
                elif not ad.verified and not ad.expired:
                    ads_not_approved = True
                elif ad.verified and ad.expired:
                    ad.verified = False
                    ad.save()
                    ads_expired = True
                    
            ads_serializer = AdSerializer(verified_ads, many=True)

            response_data = {
                'business_data': business_serializer.data,
                'ads_data': ads_serializer.data
            }
    
            if ads_not_approved:
                response_data['msg'] = 'Ads are not Approved'
            elif ads_expired:
                response_data['msg'] = 'Ads have expired'
            else:
                response_data['msg'] = 'Data fetched'

            return Response({'data': response_data}, status=status.HTTP_200_OK)



class MailRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, uid, token):
        serializer = MailRegisterSerializer(data=request.data, context={'uid': uid, 'token': token})
        if serializer.is_valid():
            user = serializer.save()

            uid = self.kwargs.get('uid')
            id = smart_str(urlsafe_base64_decode(uid))
            business = Business.objects.get(id=id)
            business.owner = user
            business.save()
            authtoken = get_tokens_for_user(user)
            return Response({'msg': 'Registered Successfully', 'token': authtoken}, status=status.HTTP_200_OK)
        else:
            return Response({'msg': 'Invalid Data'}, status=status.HTTP_400_BAD_REQUEST)
        



class UserChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Password Changed Successfully'}, status=status.HTTP_200_OK)




class UserPasswordResetMailView(APIView):
    permission_classes = [permissions.AllowAny,]

    def post(self, request):
        serializer = UserSendPasswordResetMailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Password Reset mail sent Successfully'}, status=status.HTTP_200_OK)





class UserPasswordResetView(APIView):
    permission_classes = [permissions.AllowAny,]

    def post(self, request, uid, token):
        # print(request.COOKIES.get('csrf'))
        serializer = UserPasswordResetSerializer(data=request.data, context={'uid': uid, 'token': token})
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Password Reset Successfully'}, status=status.HTTP_200_OK)







def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        forward = str(x_forwarded_for)
        ip = forward.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    return ip



def ip_view(request):
    user_ip = get_client_ip(request)
    return HttpResponse(f"User's IP address: {user_ip}")




# class GetCSRFTokenView(APIView):
#     permission_classes = [permissions.AllowAny]

#     @method_decorator(ensure_csrf_cookie)
#     def dispatch(self, *args, **kwargs):
#         return super().dispatch(*args, **kwargs)

#     def get(self, request):
#         csrf_token = get_token(request)

#         return Response({'msg': 'CSRF Cookie Set', 'csrf_token': csrf_token})
    
    


class CheckAuthenticatedView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        user = request.user

        try:
            isAuthenticated = user.is_authenticated

            if isAuthenticated:
                return Response({ 'isAuthenticated': 'True' })
            else:
                return Response({ 'isAuthenticated': 'False' })
        except:
            return Response({ 'error': 'Something went wrong when checking authentication status' })
        

# from django.http import JsonResponse
# from django.middleware.csrf import get_token

# def GetCSRFTokenView(request):
#     response = JsonResponse({"Info": "Success CSRF Cookie set"})
#     response['X-CSRFToken'] = get_token(request)

#     return response





