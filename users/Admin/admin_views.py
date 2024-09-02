from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from .admin_serializers import (
    AdminADApproveSerializer, AdminMessageViewSerializer, AdminMsgApproveSerializer,
    ListingsExcelUploadSerializer, AdminBannerApproveSerializer
    )
from Listings.models import (TextMessage, Business, BusinessMobileNumbers,
                             SubCategory, ProductService, BusinessEmailID)
from ADS.models import ADS
from Brands.models import BrandBusinessPage
from Listings.ADS.ads_serializers import AdSerializer
from Banner.serializers import BannerSerializer
from django.utils import timezone
from django.db import transaction
import pandas as pd
from Listings.models import Business, Category
from Banner.models import Banner
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
import time
import hashlib
from ..tasks import Utils
from django.shortcuts import get_object_or_404
from users.models import User
from rest_framework.parsers import MultiPartParser, FormParser
from PIL import Image as PILImage
import io
from django.core.files.uploadedfile import SimpleUploadedFile
import base64
from django.db import IntegrityError



TOKEN_EXPIRATION_SECONDS = 3600


def generate_business_token(business):
    current_time = int(time.time())
    expiration_time = current_time + TOKEN_EXPIRATION_SECONDS
    # timestamp = str(int(time.time()))
    data = f"{business.id}{expiration_time}"
    token = hashlib.sha256(data.encode()).hexdigest()
    
    encoded_token = urlsafe_base64_encode(force_bytes(token))
    return encoded_token, expiration_time



class AdminPanelAPIView(APIView):
    permission_classes = [permissions.IsAdminUser,]

    def get(self, request):
        pass


class AdminADApproveAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        ads = ADS.objects.filter(verified=False)

        ad_serializer =  AdSerializer(ads, many=True)

        response_data = {
            'ads' : ad_serializer.data,
        }

        return Response({'msg': 'Success', 'data': response_data})
    
    def put(self, request, id):
        try:
            ads = ADS.objects.get(id=id)
        except ADS.DoesNotExist:
            return Response({'msg': 'ADS Not Listed'}, status=status.HTTP_404_NOT_FOUND)
        
        ad_serializer = AdminADApproveSerializer(ads, data=request.data)
        ads = ADS.objects.get(id=id)
        ads.start_time = timezone.now()
      
        if ad_serializer.is_valid():
            ad_serializer.save()
            return Response({'msg': 'Data saved successfully'})
        return Response({'msg': 'Data saved successfully'})    


class AdminMessageApproveAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        textmessage = TextMessage.objects.all()

        msg_serializer = AdminMessageViewSerializer(textmessage, many=True)

        response_data = {
            'msg': msg_serializer.data
        }

        return Response({'msg': 'Success', 'data': response_data})
    
    def put(self, request, id):

        try:
           textmessage = TextMessage.objects.get(id=id)
        except ADS.DoesNotExist:
            return Response({'msg': 'Message Not Available'}, status=status.HTTP_404_NOT_FOUND)
        
        msg_serializer = AdminMsgApproveSerializer(textmessage, data=request.data)
        # textmessage = TextMessage.objects.get(id=id)
      
        if msg_serializer.is_valid():
            msg_serializer.save()
            return Response({'msg': 'Data saved successfully'})
        return Response({'msg': 'Invalid Data'})
    

class AdminBannerApproveAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        banner = Banner.objects.all()

        banner_serializer =  BannerSerializer(banner, many=True)

        response_data = {
            'ads' : banner_serializer.data,
        }

        return Response({'msg': 'Success', 'data': response_data})
    
    def put(self, request, id):

        try:
            banner = Banner.objects.get(id=id)
        except Banner.DoesNotExist:
            return Response({'msg': 'Banner Not Listed'}, status=status.HTTP_404_NOT_FOUND)
        
        banner_serializer = AdminBannerApproveSerializer(banner, data=request.data)
        banner.created_on = timezone.now()
      
        if banner_serializer.is_valid():
            banner_serializer.save()
            return Response({'msg': 'Data saved successfully'})
        return Response({'msg': 'Invalid Data'})
    

class AdminJobApproveAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
 

        response_data = {
            # 'jobs' : job_serializer.data,
        }
        return Response({'msg': 'Success', 'data': response_data})
    
    # def put(self, request, id):
    #     try:
    #         ads = Job.objects.get(id=id)
    #     except Banner.DoesNotExist:
    #         return Response({'msg': 'Banner Not Listed'}, status=status.HTTP_404_NOT_FOUND)
        
    #     # job_serializer = AdminJobApproveSerializer(ads, data=request.data)
    #     job = Job.objects.get(id=id)
    #     job.created_on = timezone.now()
      
    #     if job_serializer.is_valid():
    #         job_serializer.save()
    #         return Response({'msg': 'Data saved successfully'})
    #     return Response({'msg': 'Invalid Data'})  


class ListingsExcelUploadAPIView(APIView):
    permission_classes = [permissions.IsAdminUser,]
    parser_classes     = [MultiPartParser, FormParser]

    @transaction.atomic
    def post(self, request):
        serializer = ListingsExcelUploadSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        excel_file = serializer.validated_data['excel_file']

        try:
            df = pd.read_excel(excel_file)
            df = df.fillna('')
        except Exception as e:
            print(f"Error during Excel parsing: {str(e)}")
            return Response({'error': 'Failed to Parse the file'}, status=status.HTTP_400_BAD_REQUEST)

        skipped_business_names = []
        existing_user = []
        skipped_numbers = []

        for index, row in df.iterrows():
            try:
                with transaction.atomic():
                    # print(df.columns)
                    columns_to_fill = ['CIN_No', 'GSTIN', 'Company_No', 'RoC']
                    df[columns_to_fill] = df[columns_to_fill].fillna('')

                    email_id = str(row['E-mail ID'])
                    email_ids = [email_id.strip() for email_id in email_id.split(',')]
                    first_email_id = email_ids[0]

                    category_type  = row['Category']
                    established_on = row['Year of Establishment']
                    business_name  = row['Business Name']
                    email          = first_email_id
                    mobile_number  = row['Mobile No']

                    # user = User.objects.filter(email=email, mobile_number=mobile_number).first()
                    user, created = User.objects.get_or_create(
                        email         = email,
                        name          = business_name,
                        mobile_number = mobile_number,
                        business_name = business_name
                    )

                    if created:
                        business_page = Business.objects.create(owner=user)
                    else:
                        business_page = user.business
                    
                    # if pd.notna(established_on):
                    #     established_on = pd.to_datetime(established_on, errors='coerce')

                    #     if pd.notna(established_on):
                    #         established_on = established_on
                    #     else:
                    #         established_on = None
                    # else:
                    #     established_on = None

                    category, create = Category.objects.get_or_create(type=category_type)

                    sub_category       = str(row['Sub Category'])
                    sub_category_names = [name.strip() for name in sub_category.split(',')]
                    subcategories      = [
                        SubCategory.objects.get_or_create(category=category, name=name)[0] 
                                         for name in sub_category_names]

                    productservice = str(row['Product & Service'])
                    productservice_names = [name.strip() for name in productservice.split(',')]
                    productservices      = [
                        ProductService.objects.get_or_create(business=Business.objects.get(owner=user),name=name)[0]
                        for name in productservice_names
                    ]

                    extra_mobile         = str(row['Extra Mobile No\'s'])
                    extra_mobile_numbers = [names.strip() for names in extra_mobile.split(',')]
                    extra_mobiles        = [BusinessMobileNumbers.objects.get_or_create(business=Business.objects.get(owner=user), 
                                                                                        mobile_number=mobile_no)[0]
                                                                                        for mobile_no in extra_mobile_numbers]
                    extra_emailIDs = [BusinessEmailID.objects.get_or_create(business=Business.objects.get(owner=user), 
                                                                                        email=email)[0]
                                                                                        for email in email_ids]
                    
                    brand  = str(row['Brand'])
                    brands = [name.strip() for name in brand.split(',')]
                    all_brands = [
                        BrandBusinessPage.objects.get_or_create(brand_name=brand_names)[0]
                                  for brand_names in brands
                                  ]
                    
                    for brand_obj in all_brands:
                        brand_obj.category.add(category)

                    if 'state' in request.data:
                        state = request.data['state']
                    else:
                        state = row['State']
                    if 'city' in request.data:
                        city = request.data['city']
                    else:
                        city = row['City']
                    if 'pincode' in request.data:
                        pincode = request.data['pincode']
                    else:
                        pincode = row['Pin']


                    whatsapp_number = int(row['Whatsapp'])
                    if not pd.isna(whatsapp_number):
                        whatsapp_str = str(int(whatsapp_number))
                        count = len(whatsapp_str)
                        print("The number of digits in the number are:", count)

                        if count >= 12:
                            skipped_numbers.append(whatsapp_number)
                            row['Whatsapp'] = ''
                    else:
                        skipped_numbers.append(whatsapp_number)

                    # if Business.objects.filter(business_name=business_name).exists():
                    #     skipped_business_names.append(business_name)
                    #     continue

                # if user:
                #     existing_user.append(email)

                if business_page:
                    business_page.business_name   = business_name
                    business_page.category        = category
                    business_page.state           = state
                    business_page.city            = city
                    business_page.pincode         = pincode
                    business_page.address         = row['Address']
                    business_page.whatsapp_number = row['Whatsapp']
                    business_page.mobile_number   = row['Mobile No']
                    business_page.email           =  email_ids[1]
                    business_page.website_url     = row['Website']
                    business_page.GSTIN           = row['GSTIN']
                    business_page.CIN_No          = row['CIN_No']
                    business_page.RoC             = row['RoC']
                    business_page.DIN             = row['DIN']
                    business_page.company_No      = row['Company_No']
                    business_page.director        = row['Director']
                    business_page.business_info   = row['About my Business']
                    business_page.services        = row['Product & Service']
                    business_page.keywords        = row['Search']
                    business_page.established_on  = established_on
                    business_page.subcategory.set(subcategories)
                    business_page.brand.set(all_brands)
                    business_page.save()

                    uid = urlsafe_base64_encode(force_bytes(business_page.id))

                    token = generate_business_token(business_page)

            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            link = f'http://127.0.0.1:8000/api/listings/mail-register/{uid}/{token}/'

            body = 'Your Business page has been created please cklick on the link' + ' ' + link + ' '
            data = {
                'subject': 'New Business Directory',
                'body': body,
                'to_email': business_page.email
            }
            # Utils.send_mail(data)

        response_data = {'msg': 'Mail has been sent to the user'}
        if skipped_business_names:
            response_data['These Business are already exists'] = skipped_business_names
        if existing_user:
            response_data['These users are already exists and there data has been updated'] = existing_user

        return Response(response_data)

