from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.views import View

from Lead.models import BusinessPageLeadBucket, Lead, LeadBucket
from PremiumPlan.models import PremiumPlan, PremiumPlanBenefits, PremiumPlanOrder, PhonepeAutoPayOrder
from .forms import AdminExcelUploadForm
from django.http import HttpResponse
import pandas as pd
from django.db import transaction
from users.models import User
from Listings.models import (
    Business, Category, SubCategory, BusinessEmailID, 
    BusinessMobileNumbers, ProductService
                             )
from Brands.models import BrandBusinessPage
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
import time
import hashlib
from django.db.models import Q
from Admin.tasks import process_excel_file, send_email, send_whatsapp_msg_while_registration
from .serializers import UserPasswordResetAfterMailSerializer
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from django.views.generic import ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from datetime import timedelta
from Phonepe.autopay import PremiumPlanPhonepeAutoPayPayment
from django.contrib import messages
# import boto3



TOKEN_EXPIRATION_SECONDS = 6600



def is_admin(user):
    return user.is_authenticated and user.is_staff



def generate_business_token(business):
    current_time = int(time.time())
    expiration_time = current_time + TOKEN_EXPIRATION_SECONDS
    # timestamp = str(int(time.time()))
    data = f"{business.id}{expiration_time}"
    token = hashlib.sha256(data.encode()).hexdigest()
    
    encoded_token = urlsafe_base64_encode(force_bytes(token))
    return encoded_token




# @transaction.atomic
@user_passes_test(is_admin)
def AdminExcelUploadView(request):
    
    if request.method == 'POST':
        form = AdminExcelUploadForm(request.POST, request.FILES)

        if not form.is_valid():
            return HttpResponse('Invalid Excel File')
        excel_file = form.cleaned_data['excel_file']

        try:
            df = pd.read_excel(excel_file)
            df = df.fillna('')
        except Exception as e:
            print(f"Error during Excel parsing: {str(e)}")
            return HttpResponse('error: Failed to Parse the file')

        skipped_business_names = []
        existing_user = []
        skipped_numbers = []

        for index, row in df.iterrows():
            try:
                try:
                    email_id = str(row['E-mail ID'])
                    email_ids = [email_id.strip() for email_id in email_id.split(',')]
                    first_email_id = email_ids[0]

                except Exception as e:
                    return HttpResponse(f"Error while detecting the mail ID: {str(e)}")
                
                try:
                    mobile_number = row.get('Mobile No', '')

                    if not mobile_number:
                        return HttpResponse("Dont left any blank mobile number field")
                    
                    if mobile_number and len(str(mobile_number)) > 15:
                        skipped_numbers.append(mobile_number)
                        return HttpResponse(f'Error: Mobile number in row {index + 2} has more than 15 digit')

                    # if isinstance(mobile_number_raw, str):
                    #     mobile_number = mobile_number_raw
                    # elif isinstance(mobile_number_raw, int):
                    #     mobile_number = mobile_number_raw
                    # else:
                    #     mobile_number = None

                except:
                    return HttpResponse(f"""Please provide a valid mobile number(Number Should be less than 12 Digit) and 
                            donot left blank space While Uploading the Mobile Number in row {index + 2}:{','.join(map(str, skipped_numbers))}""")
                
                try:
                    category_type     = row.get('Category', '')
                    established_on    = row.get('Year of Establishment', '')
                    # established_on    = int(established_on_raw) if established_on_raw.isdigit() else None
                    # if established_on_raw.isdigit():  # Check if it's a non-empty string containing only digits
                    #     established_on_int = int(established_on_raw)
                    #     established_on = established_on_int
                    # else:
                    #     established_on = None
                    # established_on    = established_on_int
                    # established_on    = row.get('Year of Establishment', '')
                    business_name     = row.get('Business Name', '')

                    email             = first_email_id
                    state             = row.get('State', '')
                    city              = row.get('City', '')
                    pincode           = row.get('Pin', '')
                    Director          = row.get('Director', '')
                    About_my_Business = row.get('About my Business', '')
                    Product_Service   = row.get('Product & Service', '')
                    Search            = row.get('Search', '')
                    Website           = row.get('Website', '')
                    Address           = row.get('Address', '')

                except Exception as e:
                    return HttpResponse(f"Error While getting the value from excel data: {str(e)}")
                
                try:
                    CIN_No                = row.get('CIN_No', '')
                    GSTIN                 = row.get('GSTIN', '')
                    DIN                   = row.get('DIN', '')
                    Company_No            = row.get('Company_No', '')
                    RoC                   = row.get('RoC', '')
                except Exception as e:
                    return HttpResponse(f"Error while fetching the CIN, DIN, GSTIN, Company_No, WhatsApp and RoC: {str(e)}")
                
                try:
                    whatsapp_number = row.get('Whatsapp', '')
                    # whatsapp_number = row.get('Whatsapp', '')

                    # if isinstance(whatsapp_number_raw, str):
                    #     # whatsapp_number = int(whatsapp_number_raw) if whatsapp_number_raw.isdigit() else None
                    #     whatsapp_number = whatsapp_number_raw
                    # elif isinstance(whatsapp_number_raw, int):
                    #     whatsapp_number = whatsapp_number_raw
                    # else:
                    #     whatsapp_number = None
                        
                    if whatsapp_number and len(str(whatsapp_number)) > 15:
                        skipped_numbers.append(whatsapp_number)
                        return HttpResponse(f'Error: Whatsapp number in row {index + 2} has more than 15 digit')

                except Exception as e:
                    return HttpResponse(f'Error while getting whatsapp number value: {str(e)}' )
                
                try:
                    user = User.objects.filter(
                            Q(mobile_number=mobile_number) | 
                            Q(email=email) 
                            ).first()

                    if not user:
                        user, created = User.objects.get_or_create(
                            email=email,
                            mobile_number=mobile_number,
                            business_name=business_name,
                            name=business_name
                        )

                    else:
                        created = False
                    
                    user.mobile_number = mobile_number
                    user.email         = email
                    user.name          = business_name
                    user.business_name = business_name
                    user.save()

                except Exception as e:
                    skipped_business_names.append(business_name)
                    return HttpResponse(f'User not created due to duplicate key error: {str(e)}')

                # if created:
                #     business_page = Business.objects.create(owner=user, business_name=business_name)
                # else:
                #     try:
                #         business_page = Business.objects.get(owner=user)
                #     except Exception as e:
                #         # pass
                #         return HttpResponse(f'Not able to Found the Business page {str(e)}')
                
                #Category
                category, create = Category.objects.get_or_create(type=category_type)
                
                #Subcategory
                try:
                    sub_category           = str(row.get('Sub Category', ''))
                    if sub_category:
                        sub_category_names = [name.strip() for name in sub_category.split(',')]
                        subcategories      = [
                            SubCategory.objects.get_or_create(category=category, name=name)[0]
                                                for name in sub_category_names]
                    else:
                        subcategories = None
                        # subcategories = []
                except Exception as e:
                    subcategories = None
                    # pass
                    return HttpResponse(f"Error While Saving Sub Category Please check the data format: {str(e)}")
                
                #Product and Service
                try:
                    productservice = str(row.get('Product & Service', ''))
                    if productservice:
                        productservice_names = [name.strip() for name in productservice.split(',')]
                        productservices      = [
                            ProductService.objects.get_or_create(business=Business.objects.get(owner=user),name=name)[0]
                            for name in productservice_names
                        ]
                    else:
                        productservices = []
                except Exception as e:
                    productservices = []
                    # return HttpResponse(f"Error while Saving the Product and Service Please check the data format: {str(e)}")

                
                #Extra Mobile Numbers
                try:
                    extra_mobile         = str(row.get('Extra Mobile No\'s', ''))
                    if extra_mobile:
                        extra_mobile_numbers = [names.strip() for names in extra_mobile.split(',')]
                        try:
                            business      = Business.objects.get(business_name=business_name)
                            extra_mobiles = [BusinessMobileNumbers.objects.get_or_create(business=Business.objects.get(owner=business),
                                                                                                mobile_number=mobile_no)[0]
                                                                                                for mobile_no in extra_mobile_numbers]
                        except:
                            extra_mobiles = []
                    else:
                        extra_mobiles = []

                except Exception as e:
                    extra_mobiles = []
                    

                #Extra Mail IDs
                try:
                    extra_emailIDs = []
                    for email in email_ids[1:]:
                        existing_email = BusinessEmailID.objects.filter(business__owner=user, email=email).first()

                        if not existing_email:
                            new_email_id = BusinessEmailID.objects.create(
                                business=Business.objects.get(owner=user),
                                email=email
                            )
                            extra_emailIDs.append(new_email_id)
                except:
                    extra_emailIDs = []

                #Brands
                try:
                    brand  = str(row.get('Brand', ''))
                    if brand:
                        brands = [name.strip() for name in brand.split(',')]
                        all_brands = [
                            BrandBusinessPage.objects.get_or_create(brand_name=brand_names)[0]
                                        for brand_names in brands
                                        ]

                        for brand_obj in all_brands:
                            brand_obj.category.add(category)
                    else:
                        all_brands = None
                        # all_brands = []

                except:
                    all_brands = None

                try:
                    business_page = Business.objects.filter(
                        Q(mobile_number = mobile_number) |
                        Q(email         = email) 
                        # Q(business_name = business_name) |
                        # Q(GSTIN         = GSTIN) |
                        # Q(CIN_No        = CIN_No) |
                        # Q(company_No    = Company_No) |
                        # Q(DIN           = DIN) 
                    ).first()

                    if not business_page:
                        try:
                            business_page = Business.objects.create(
                                owner = user,
                                mobile_number = mobile_number,
                                email = email
                            )

                            if GSTIN:
                                business_page.GSTIN = GSTIN
                            if CIN_No:
                                business_page.CIN_No  = CIN_No
                            if DIN:
                                business_page.DIN    = DIN
                            if whatsapp_number:
                                business_page.whatsapp_number = whatsapp_number
                            if Company_No:
                                business_page.company_No = Company_No
                            if established_on:
                                business_page.established_on = established_on

                            business_page.business_name = business_name
                            business_page.category = category
                            business_page.state = state
                            business_page.city = city
                            business_page.pincode = pincode
                            business_page.address = Address
                            business_page.website_url = Website
                            business_page.director  = Director
                            business_page.business_info = About_my_Business
                            business_page.services = Product_Service
                            business_page.keywords = Search
                            # business_page.subcategory.set(subcategories)
                            # business_page.brand.set(all_brands)

                            # uid   = urlsafe_base64_encode(force_bytes(business_page.business_name))
                            # link = f'https://famousbusiness.in/userprofile/{business_page.business_name}?z_id={business_page.pk}&mail=mail&uuid={uid}'

                            # data = {
                            #     'subject': 'Elevate Your Business with Exclusive PAN India Leads',
                            #     'to_email': user.email,
                            #     'link': link,
                            #     'business_name': business_page.business_name,
                            #     'mobile_number': business_page.mobile_number,
                            #     'business_category': business_page.category.type
                            #     }

                            # send_email.delay(data)
                            # send_whatsapp_msg_while_registration.delay(data)
                            
                        except Exception as e:
                            return HttpResponse(f"Error While creating business page: {str(e)}")

                    try:
                        business_page.mobile_number = mobile_number
                    except Exception as e:
                        return HttpResponse(f"Error while assigning mobile number to Business Page: {str(e)}")
                    
                    try:
                        business_page.business_name   = business_name
                    except Exception as e:
                        return HttpResponse(f"Error while assigning business name to business page {str(e)}")
                    
                    try:
                        if whatsapp_number:
                            business_page.whatsapp_number = whatsapp_number
                    except Exception as e:
                        return HttpResponse(f"Error while assigning Whats app number to business page {str(e)}")
                    
                    try:
                        business_page.email           = first_email_id    
                    except Exception as e:
                        return HttpResponse(f"Error while assigning Email ID to business page {str(e)}")
                    
                    try:
                        if GSTIN:
                            business_page.GSTIN          = GSTIN
                    except Exception as e:
                        return HttpResponse(f"GST ERROR: {str(e)}")
                    
                    try:
                        if CIN_No:
                            business_page.CIN_No          = CIN_No
                    except Exception as e:
                        return HttpResponse(f"CIN No ERROR: {str(e)}")
                    
                    try:
                        if DIN:
                            business_page.DIN             = DIN
                    except Exception as e:
                        return HttpResponse(f"DIN Error: {str(e)}")
                    
                    try:
                        if Company_No:
                            business_page.company_No      = Company_No   
                    except Exception as e:
                        return HttpResponse(f"Company No. Error: {str(e)}")
                    
                    try:
                        business_page.RoC             = RoC
                    except Exception as e:
                        return HttpResponse(f"Roc Error: {str(e)}")
                    
                    try:
                        if established_on:
                            business_page.established_on  = established_on
                    except Exception as e:
                        return HttpResponse(f"established on Error: {str(e)}")
                    
                    business_page.category        = category
                    business_page.state           = state
                    business_page.city            = city
                    business_page.pincode         = pincode
                    business_page.address         = Address
                    business_page.website_url     = Website
                    business_page.director        = Director
                    business_page.business_info   = About_my_Business
                    business_page.services        = Product_Service
                    business_page.keywords        = Search
                    # business_page.subcategory.set(subcategories)
                    # business_page.brand.set(all_brands)
                    business_page.save()

                    uid   = urlsafe_base64_encode(force_bytes(business_page.business_name))
                    link = f'https://famousbusiness.in/userprofile/{business_page.business_name}?z_id={business_page.pk}&mail=mail&uuid={uid}'

                    data = {
                        'subject': 'Elevate Your Business with Exclusive PAN India Leads',
                        'to_email': user.email,
                        'link': link,
                        'business_name': business_page.business_name,
                        'mobile_number': business_page.mobile_number,
                        'business_category': business_page.category.type
                        }
                    
                    # send_email.delay(data)
                    send_whatsapp_msg_while_registration.delay(data)

                except Exception as e:
                    return HttpResponse(f"Business Page Error: {str(e)}")

            except Exception as e:
                return HttpResponse(f'error while saving data {str(e)}')
            

        if skipped_numbers:
            return HttpResponse(f'Mobile numbers with more than 15 digits: {", ".join(map(str, skipped_numbers))}')

    # response_data = {'msg': 'Mail has been sent to the user'}

    return render(request, 'Admin/excel_upload.html')



@user_passes_test(is_admin)
def ExcelUploadView(request):
    
    if request.method == 'POST':
        form = AdminExcelUploadForm(request.POST, request.FILES)

        if not form.is_valid():
            return HttpResponse('Invalid Excel File')
        excel_file = form.cleaned_data['excel_file']

        try:
            df = pd.read_excel(excel_file)
            df = df.fillna('')
        except Exception as e:
            return HttpResponse('error: Failed to Parse the file')

        skipped_business_names = []
        existing_user = []
        skipped_numbers = []

        for index, row in df.iterrows():
            try:
                mobile_number = row.get('Mobile No', '')

                if not mobile_number:
                    return HttpResponse("Dont left any blank mobile number field")
                
                if mobile_number and len(str(mobile_number)) > 15:
                    skipped_numbers.append(mobile_number)
                    return HttpResponse(f'Error: Mobile number in row {index + 2} has more than 15 digit')

            except:
                return HttpResponse(f"""Please provide a valid mobile number(Number Should be less than 12 Digit) and 
                        donot left blank space While Uploading the Mobile Number in row {index + 2}:{','.join(map(str, skipped_numbers))}""")
            
            try:
                category_type     = row.get('Category', '')
                business_name     = row.get('Business Name', '')
                state             = row.get('State', '')
                city              = row.get('City', '')
                pincode           = row.get('Pin', '')
                Address           = row.get('Address', '')
                Website           = row.get('Website', '')

            except Exception as e:
                    return HttpResponse(f"Error While getting the value from excel data: {str(e)}")
            
            # Get or create user from mobile number
            try:
                user, created = User.objects.get_or_create(
                    mobile_number = mobile_number)
            except Exception as e:
                return HttpResponse("Error while detecting email")
            
            if user:
                user.name          = business_name
                user.business_name = business_name

                user.save()
                
            #Category
            category, create = Category.objects.get_or_create(type=category_type)

            try:
                # Create Business page
                business_page, created = Business.objects.get_or_create(
                    owner = user
                )

                if business_page:
                    business_page.business_name = business_name
                    business_page.mobile_number = mobile_number
                    business_page.whatsapp_number = mobile_number
                    business_page.category      = category
                    business_page.state         = state
                    business_page.city          = city
                    business_page.pincode       = pincode
                    business_page.address       = Address
                    business_page.website_url   = Website
                    business_page.save()

                    uid   = urlsafe_base64_encode(force_bytes(business_page.business_name))
                    link = f'https://famousbusiness.in/userprofile/{business_page.business_name}?z_id={business_page.pk}&mail=mail&uuid={uid}'

                    data = {
                        'subject': 'Elevate Your Business with Exclusive PAN India Leads',
                        'to_email': user.email,
                        'link': link,
                        'business_name': business_page.business_name,
                        'mobile_number': business_page.mobile_number,
                        'business_category': business_page.category.type
                        }
                    
                    send_whatsapp_msg_while_registration.delay(data)

            except Exception as e:
                return HttpResponse(f"Error while assigning mobile number to Business Page: {str(e)}")
            
    return render(request, 'Admin/excel_upload.html')







def AdminDashBoardView(request):
    return render(request, 'Admin/home_page.html')






class PasswordResetAfterMailView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, uid):
        serializer = UserPasswordResetAfterMailSerializer(data=request.data, context={'uid': uid})
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Password Reset Successfully'}, status=status.HTTP_200_OK)



class AWSBounceMailListView(View):
    pass
#     def get(self, request, *args, **kwargs):
#         aws_access_key        = config('AWS_ACCESS_KEY_ID')
#         aws_secret_access_key = config('AWS_SECRET_ACCESS_KEY')
#         aws_region            = config('AWS_REGION')

#         ses_v2_client = boto3.client('sesv2', aws_access_key_id=aws_access_key, 
#                                   aws_secret_access_key=aws_secret_access_key,
#                                   region_name=aws_region)
#         response = ses_v2_client.list_suppressed_destinations()

#         suppression_list = response.get('SuppressedDestinationSummaries', [])

#         context = {'suppression_list': suppression_list}

#         return render(request, 'Admin/aws_email_list.html', context)



class UsersPurchasedLeadView(View):

    def get(self, request):
        users_purchased_lead = LeadBucket.objects.all().order_by('-id')

        return render(request, 'Lead/users_po_lead.html', {'purchased_lead': users_purchased_lead})
    

class BusinessOwnerPurchasedLeadView(View):

    def get(self, request):
        businesses_purchased_lead = BusinessPageLeadBucket.objects.all().order_by('-id')

        return render(request, 'Lead/business_lead_po.html', {'purchased_lead': businesses_purchased_lead})
    

class AllLeadView(View):
    def get(self, request, *args, **kwargs):
        all_leads = Lead.objects.all()
        return render(request, 'Lead/all_lead.html', {'all_leads': all_leads})

    def post(self, request, *args, **kwargs):
        return HttpResponse('POST request!')


class PurchasedPremiumPlanView(View):

    def get(self, request):
        purchased_plans = PremiumPlanBenefits.objects.all().order_by('-id')

        return render(request, 'PremiumPlan/purchased_plan.html', {'purchased_plan': purchased_plans})



class PremumPlanOrderView(View):

    def get(self, request):
        plan_orders = PremiumPlanOrder.objects.all().order_by('-id')

        return render(request, 'PremiumPlan/orders.html', {'plan_orders': plan_orders})
    


class AllActivePremiumPlanView(View):

    def get(self, request):
        plans = PremiumPlan.objects.all().order_by('-id')

        return render(request, 'PremiumPlan/plans.html', {'plans': plans})
    



class AllUsersDetailView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'User/users.html'
    context_object_name = 'all_users'
    ordering = ['-id']
    paginate_by = 100


    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def post(self, request):
        searched_value = request.POST.get("Search")

        q_objects = (
            Q(email__icontains=searched_value) |
            Q(mobile_number__icontains=searched_value) |
            Q(name__icontains=searched_value) |
            Q(business_name__icontains=searched_value)
        )

        all_users = User.objects.filter(q_objects).order_by('-id')

        return render(request, 'User/users.html', {'all_users': all_users})


class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    template_name = 'User/user_update.html'
    fields = "__all__"
    success_url = "/all-users"

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff
    



class AllBusinessPageDetailView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Business
    template_name = 'User/business_page.html'
    context_object_name = 'all_business'
    ordering = ['-id']
    paginate_by = 100
    

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def post(self, request):
        searched_value = request.POST.get("Search")

        q_objects = (
            Q(email__icontains=searched_value) |
            Q(mobile_number__icontains=searched_value) |
            Q(GSTIN__icontains=searched_value) |
            Q(business_name__icontains=searched_value)
        )

        all_business = Business.objects.filter(q_objects).order_by('-id')

        return render(request, 'User/business_page.html', {'all_business': all_business})
    
    
class BusinessUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Business
    template_name = 'User/business_update.html'
    fields = "__all__"
    success_url = "/all-business"

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff



def LoginRedirectView(request):
    return HttpResponse("Logged in Successfully")


def GoogleLoginView(request):
    return render(request, 'User/google_login.html')


#### Deduct Monthly Payment
class DuductPeriodicPaymentView(LoginRequiredMixin, ListView):
    model = PremiumPlanOrder
    template_name = 'PremiumPlan/deduct_payment.html'


    def post(self, request):
        try:
            orders_to_deduct = PremiumPlanOrder.objects.all()
        except Exception as e:
            return Response({'message': 'Premium plan does not exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        current_date = timezone.now()

        try:
            recurring_payment = PremiumPlanPhonepeAutoPayPayment.RecurringInit(
                            'OMS2410122346089614518068D',
                            9,
                            '89ee1cfa-a59b-4289-a'
                    )
        except Exception as e:
            messages.error(request, f'Error {str(e)}')
        
        if recurring_payment and recurring_payment['success'] == True:
            # order = PremiumPlanOrder.objects.get(transaction_id = '89ee1cfa-a59b-4289-a')
            # order.payment_response = str(recurring_payment)
            # order.save()

            messages.success(request, "successfully deduct the amount")

        messages.success(request, "Not able to deduct the amount")

        # try:
        #     for order in orders_to_deduct:
        #         days_since_purchase = (current_date - order.purchased_at).days
        #         transactionID = order.transaction_id
                
        #         if days_since_purchase >= 29:
                    
        #             try:
        #                 transactionID = order.transaction_id
        #                 phonepe_order = PhonepeAutoPayOrder.objects.get(authRequestId=transactionID)

        #                 subscriptionID = phonepe_order.subscriptionId
        #                 amount         = phonepe_order.amount
        #             except Exception as e:
        #                 messages.error(request, "Not able to get the Phonepe order")

        #             try:
        #                 recurring_payment = PremiumPlanPhonepeAutoPayPayment.RecurringInit(
        #                     subscriptionID,
        #                     amount,
        #                     transactionID
        #                 )

        #                 if recurring_payment and recurring_payment['success'] == True:
        #                     order.payment_response         = str(recurring_payment)
        #                     phonepe_order.payment_response = str(recurring_payment)
        #                     phonepe_order.save()
        #                     order.save()

        #             except Exception as e:
        #                 # return Response({'message': f'{str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        #                 return messages.error(request, f"Problem occured while deducting payment - {str(e)}")

        #             # If everything succeeds, show success message
        #             messages.success(request, f'Successfully processed orders')

        #         else:
        #             messages.success(request, 'Payment time has not reached yet')

        # except Exception as e:
        #     messages.error(request, f'Phonepe AutoPay order does not exist {str(e)}')
            
        # except Exception as e:
        #     messages.error(request, f'An error occurred: {str(e)}')

        # Return count or error message to the template
        return render(request, self.template_name)
    


# from rest_framework.generics import GenericAPIView
# class GoogleSocialAuthView(GenericAPIView):

#     serializer_class = GoogleSocialAuthSerializer

#     def post(self, request):
#         """

#         POST with "auth_token"

#         Send an idtoken as from google to get user information

#         """

#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         data = ((serializer.validated_data)['auth_token'])
#         return Response(data, status=status.HTTP_200_OK)
