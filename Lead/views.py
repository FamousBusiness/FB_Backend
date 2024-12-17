import contextlib
from celery import group
from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework import permissions
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from Listings.models import (
    Category, Business,
    )
from Lead.models import (
    BusinessPageLeadView, Lead, BusinessPageLeadBucket, BusinessPageLead, AssignedLeadPerPremiumPlan, 
    LeadBucket, LeadPrice, ComboLead, ComboLeadBucket, LeadOrder, LeadFrorm,
    BusinessPageEnquiredLeadViews, ComboLeadOrder, LeadBanner
    )
from .serializer import (BusinessPageleadViewSerializer, LeadSerializer, LeadPaymentSerializer,PriceLeadWithoutAllDataSerializer,
            IndividualLeadsSerializer, EnquiryFormSerializer, BusinessPageLeadSerializer,
            LeadWithoutAllDataSerializer, IndividualPageLeadWithoutAllDataSerializer,
            PaidLeadSerializers, LeadExcelUploadFrom, ComboLeadPaymentSerializer,
            ComboLeadSerializer, AssignedPremiumPlanLeadSerializer, UsersPaidLeadSerializer, GetLeadFormSerializer, LeadBannerSerializer
    )
from rest_framework import status, generics
from Listings.RazorpayPayment.razorpay.main import RazorpayClient
from .task import (
    Lead_purchase_mail, beat_task_to_send_lead_mail_every_10_minute, send_business_page_lead_mail, send_category_wise_business_message_excel_upload, send_category_wise_business_whatsapp_message_lead_excel_upload, send_lead_mail_to_category_wise_business,send_category_wise_business_mail_excel_upload,
    send_mail_for_remaining_combo_lead, send_category_wise_business_whatsapp_message_enquiry_form_submit, send_whatsapp_message_enqiury_form_user
    )
import pandas as pd
from django.views import View
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from PremiumPlan.models import PremiumPlanBenefits, TrialPlanRequest
from django.db.models import Sum
from rest_framework.pagination import PageNumberPagination
from django.db.models import F
from Lead.phonepe_payment import LeadPaymentInitiation, ComboLeadPaymentInitiation
from decouple import config
from Phonepe.payment import calculate_sha256_string
import requests
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.utils.decorators import method_decorator
from users.models import User





CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)
rz_client = RazorpayClient()




#Payment initiation To Purchase a Lead
class LeadPaymentAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def post(self, request):
        serializer = LeadPaymentSerializer(data=request.data)

        if serializer.is_valid():
            received_amount = serializer.validated_data.get('amount')
            amount          = received_amount * 100
            current_user    = request.user
            lead_id         = serializer.validated_data.get('lead_id')

            try:
                lead_instance = Lead.objects.get(id=lead_id)
                lead_instance_id = lead_instance.pk
            except Lead.DoesNotExist:
                return Response({'msg': 'Requested Lead doesnot exist'}, status=status.HTTP_404_NOT_FOUND)
            
            try:
                try:
                    lead_bucket = LeadBucket.objects.get(owner=current_user, lead_id=lead_instance_id)
                except ObjectDoesNotExist:
                    try:
                        lead_bucket = BusinessPageLeadBucket.objects.get(business_page__owner=current_user.id, lead=lead_id)
                    except ObjectDoesNotExist:
                        lead_bucket = None

                if lead_bucket:
                    return Response({'msg': 'The user has already purchased the lead'})
            except Exception:
                pass


            try:
                order = LeadOrder.objects.create(user=current_user, amount=received_amount)
                transaction_id = order.transaction_id

                payment_response = LeadPaymentInitiation(transaction_id, amount, lead_instance_id)
                return Response({'msg': 'Payment initiation successful', 'payment_response': payment_response},
                                status=status.HTTP_200_OK)
            
            except LeadOrder.DoesNotExist:
                return Response({'msg': 'Lead order does not get created'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            
        else:
            response = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "bad request",
                "error": serializer.errors
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)   



@csrf_exempt
def LeadPaymentCompleteView(request):
    lead_id      = request.GET.get('lead')
    INDEX        = "1"
    SALTKEY      = config("SALT_KEY")

    payment_status = request.POST.get('code', None)
    merchant_id = request.POST.get('merchantId', None)
    transaction_id = request.POST.get('transactionId', None)
    amount = request.POST.get('amount', None)
    check_sum = request.POST.get('checksum', None)
    provider_reference_id = request.POST.get('providerReferenceId', None)
    merchant_order_id = request.POST.get('merchantOrderId', None)

    if transaction_id:
        request_url = 'https://api.phonepe.com/apis/hermes/status/FBM225/' + transaction_id
        sha256_Pay_load_String = '/pg/v1/status/FBM225/' + transaction_id + SALTKEY
        sha256_val = calculate_sha256_string(sha256_Pay_load_String)
        checksum = sha256_val + '###' + INDEX

        headers = {
            'Content-Type': 'application/json',
            'X-VERIFY': checksum,
            'X-MERCHANT-ID': transaction_id,
        }

        response = requests.get(request_url, headers=headers)

        try:
            order = LeadOrder.objects.get(transaction_id=transaction_id)
        except LeadOrder.DoesNotExist:
            response_data = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Client Order with the specified provider_order_id not found",
                }
            return redirect("https://www.famousbusiness.in/leads")
        
        order.provider_reference_id = provider_reference_id
        order.merchant_id           = merchant_id
        order.checksum              = check_sum
        order.status                = payment_status
        order.isPaid                = True
        order.details               = f'Purchased a lead of of ID:> {lead_id}'
        order.message               = response.text
        order.merchant_order_id     = merchant_order_id
        user                        = order.user
        order.save()

        if payment_status == "PAYMENT_SUCCESS":

            try:
                lead = Lead.objects.get(id=lead_id)
            except Lead.DoesNotExist:
                return redirect("https://www.famousbusiness.in/leads")
            
            try:
                business_page = Business.objects.get(owner=order.user)

                if business_page:
                    BusinessPageLeadBucket.objects.create(business_page=business_page, is_paid=True, lead=lead)
                    lead.views += 1
                    lead.save()

                    data = {
                    'email': business_page.email,
                    'transaction_id': transaction_id,
                    'name': business_page.business_name,
                    'amount': order.amount
                    }
                    Lead_purchase_mail.delay(data)
                    
            except Exception:
                LeadBucket.objects.create(owner=order.user, is_paid=True, lead = lead, viewed= True)
                lead.views += 1
                lead.save()
                
                data = {
                    'email': user.email,
                    'transaction_id': transaction_id,
                    'name': user.name,
                    'amount': order.amount
                    }
                Lead_purchase_mail.delay(data)
                return redirect("https://www.famousbusiness.in/success")

            return redirect("https://www.famousbusiness.in/success")
        else:
            return redirect("https://www.famousbusiness.in/failure")

    return redirect("https://www.famousbusiness.in/failure")
 
    


#Already used on Category wise Business 

# class CategoryLeadApiView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def can_create_lead(self, user, category):
#       current_time = timezone.now()

#       six_hours_ago = current_time - timedelta(hours=6)
#       existing_leads = Lead.objects.filter(created_by=user, category=category, created_at__gte=six_hours_ago).exists()

#       return not existing_leads
    
#     def post(self, request):
#         user = request.user
#         category_id  = request.data.get('category')
#         category = Category.objects.get(pk=category_id) if category_id else None

#         lead_serializer = CategoryLeadGenerateSerializer(data=request.data)
#         lead_serializer.is_valid(raise_exception=True)

#         if category and not self.can_create_lead(user, category):
#             return Response({'msg': 'Cannot create lead in the same category within 6 hours'}, status=status.HTTP_201_CREATED)
#         else:
#             # lead_serializer.save(created_by = user)
#             return Response({'msg': 'Lead generated successfully'}, status=status.HTTP_400_BAD_REQUEST)    



#Enquiry form without any specific user(Business Page)
class EnquiryFormAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        enquiry_serializer = EnquiryFormSerializer(data=request.data)
        enquiry_serializer.is_valid(raise_exception=True)

        name          = enquiry_serializer.validated_data.get('name')
        mobile_number = enquiry_serializer.validated_data.get('mobile_number')
        category      = enquiry_serializer.validated_data.get('category')
        requirements  = enquiry_serializer.validated_data.get('requirements')
        city          = enquiry_serializer.validated_data.get('city')
        state         = enquiry_serializer.validated_data.get('state')
        email         = request.data.get('email')
        pincode       = request.data.get('pincode')


        try:
            lead_price = LeadPrice.objects.get(id=2)
        except Exception as e:
            return Response("Assign a price to the lead")
        
        # user = request.user

        lead = Lead.objects.create(
            created_by    = name,
            mobile_number = mobile_number,
            category      = category,
            status        = 'High Priority',
            requirement   = requirements, 
            price         = lead_price,
            state         = state,
            city          = city,
            email         = email,
            pincode       = pincode
        )

        # Create user using Mobile Number
        try:
            user, created = User.objects.get_or_create(
                mobile_number = mobile_number,
                name          = name
            )

            if created:
                data = [{
                'user_name': lead.created_by,
                'lead_id': lead.pk, 
                'mobile_number': mobile_number
                }]
                send_whatsapp_message_enqiury_form_user.delay(data)

        except Exception as e:
             pass

        business_pages = Business.objects.filter(category=category, city=city).values('email', 'business_name', 'mobile_number')

        if not business_pages:
            return Response({'msg': 'No more businesses available for the given criteria.'}, status=status.HTTP_200_OK)
        
        # tasks = []

        data = [{
                'business_email': business['email'],
                'business_name': business['business_name'],
                'location': lead.city, 
                'customer_name': lead.created_by,
                'requirements': lead.requirement, 
                'mobile_number': business['mobile_number']
            } for business in business_pages]
        
        # send_lead_mail_to_category_wise_business.delay(data)
        # tasks.append(send_category_wise_business_whatsapp_message_lead_excel_upload.s(data))
        # tasks.append(send_category_wise_business_message_excel_upload.s(data))
        send_category_wise_business_whatsapp_message_enquiry_form_submit.delay(data)
        
        # group(*tasks).apply_async()

        return Response({'Msg':'Lead Created Succefully'}, status=status.HTTP_201_CREATED)




#Generate Lead for Specific Business Page Enquiry
class BusinessPageLeadAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # user = request.user
        try:
            business_page_id = request.data.get('business_id')
            business_instance = Business.objects.get(id=business_page_id)

            enquiry_serializer = BusinessPageLeadSerializer(data=request.data)
            enquiry_serializer.is_valid(raise_exception=True)

            name = enquiry_serializer.validated_data.get('name')
            mobile_number = enquiry_serializer.validated_data.get('mobile_number')
            requirements  = enquiry_serializer.validated_data.get('requirements')

            BusinessPageLead.objects.create(
                business_page = business_instance,
                created_by    = name,
                requirement   = requirements,
                mobile_number = mobile_number,
                status        = 'High Priority'
            )

            business_data = {
                'id': business_instance.id,
                'business_name': business_instance.business_name,
                'email': business_instance.email,
            }
            data = {
                'lead_mobile_number': mobile_number,
                'lead_name': name,
                'lead_requirements': requirements,
                'business': business_data,
            } 

            send_business_page_lead_mail.delay(data)

        except Exception as e:
            return Response({'msg': f'Error: {str(e)}'})
        return Response({'Msg':'Lead Created Succefully'}, status=status.HTTP_201_CREATED)
    

    #Get all Specific Business Page Lead
    def get(self, request):
        user = request.user
        business = Business.objects.get(owner=user)

        individual_leads = BusinessPageLead.objects.filter(business_page=business)

        serializer = IndividualLeadsSerializer(individual_leads, many=True)

        return Response({'msg': 'Success', 'data': serializer.data})     



#All Lead Data
class AllLeadWithoutAllDataView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    pagination_class   = PageNumberPagination
    page_size = 1


    def get(self, request, state, city):
        user = request.user
        response_data = {}

        if user.is_authenticated:
            user_name = user.name

            try:
                user_specific_lead = Lead.objects.filter(created_by=user_name)
                all_leads = Lead.objects.all()

                if user_specific_lead:
                    if city:
                        leads = all_leads.filter(city__iexact=city).exclude(id__in=[user_leads.id for user_leads in user_specific_lead])
                    elif state:
                        leads = all_leads.filter(state__iexact=state).exclude(id__in=[user_leads.id for user_leads in user_specific_lead])
                else:
                    if city:
                        leads = all_leads.filter(city__iexact=city) 
                    elif state:
                        leads = all_leads.filter(state__iexact=state)

            except Exception as e:
                return Response({'msg': 'No Lead Available in this Location'}, status=status.HTTP_204_NO_CONTENT)
            

            try:
                business_page     = Business.objects.get(owner=user)
                business_category = business_page.category

                if business_page:
                    business_page     = Business.objects.get(owner=user)
                    business_category = business_page.category
                    assigned_premium_plan_leads_serializer = None

                    try:
                        available_plan = PremiumPlanBenefits.objects.filter(user=user)
                        available_plan_lead = available_plan.aggregate(total_lead=Sum('lead_assigned'))['total_lead']
                    except PremiumPlanBenefits.DoesNotExist:
                        available_plan_lead = 0

                    try:
                        trial_plan = TrialPlanRequest.objects.filter(user=user, is_active=True)
                        available_trial_plan_lead = trial_plan.aggregate(total_lead=Sum('lead_view'))['total_lead']
                    except TrialPlanRequest.DoesNotExist:
                        available_trial_plan_lead = 0

                    total_available_lead = (available_plan_lead or 0) + (available_trial_plan_lead or 0)

                    try:
                        assigned_premium_plan_lead = AssignedLeadPerPremiumPlan.objects.get(user=user)
                    except AssignedLeadPerPremiumPlan.DoesNotExist:
                        assigned_premium_plan_lead = None

                    try:
                        viewed_lead = BusinessPageLeadView.objects.filter(business_page=business_page)
                    except BusinessPageLeadView.DoesNotExist:
                        viewed_lead = None

                    individual_leads = BusinessPageLead.objects.filter(business_page=business_page)
                    paid_leads       = BusinessPageLeadBucket.objects.filter(business_page=business_page.pk)

                    if assigned_premium_plan_lead is not None:
                        assigned_premium_plan_leads_serializer = AssignedPremiumPlanLeadSerializer(assigned_premium_plan_lead)

                    unpaid_leads = leads.filter(category=business_category).exclude(id__in = [business_lead_bucket.lead.id     
                                                                                                                                                                                                                             for business_lead_bucket in paid_leads])
                    
                    assigned_leads_per_plan = AssignedLeadPerPremiumPlan.objects.all()
                    assigned_leads_ids      = assigned_leads_per_plan.values_list('lead_id', flat=True)

                    if viewed_lead is not None:
                        viewed_lead_ids = viewed_lead.values_list('lead_id', flat=True)
                        unpaid_leads    = unpaid_leads.exclude(id__in=viewed_lead_ids)

                    filtered_lead  = unpaid_leads.exclude(id__in=assigned_leads_ids)
    
                    if total_available_lead > 0:
                        category_leads_pagination = self.paginate_queryset(filtered_lead)
                        lead_serializer  = LeadWithoutAllDataSerializer(category_leads_pagination, many=True)

                    else:
                        category_leads_pagination = self.paginate_queryset(filtered_lead)
                        lead_serializer  = PriceLeadWithoutAllDataSerializer(category_leads_pagination, many=True)
                    
                    print(self.paginator.get_next_link())

                    other_category_leads = leads.exclude(category=business_category)

                    other_category_leads_wo_paid_leads = other_category_leads.exclude(id__in = [business_lead_bucket.lead.id for   business_lead_bucket in paid_leads])
                    
                    other_category_leads_wo_assigned_premium_plan_lead = other_category_leads_wo_paid_leads.exclude(id__in=assigned_leads_ids)

                    other_category_leads        = self.paginate_queryset(other_category_leads_wo_assigned_premium_plan_lead)
                    paid_leads_pagination       = self.paginate_queryset(paid_leads)
                    individual_leads_pagination = self.paginate_queryset(individual_leads)
                    viewed_lead_pagination      = self.paginate_queryset(viewed_lead)

                    other_category_serializer   = PriceLeadWithoutAllDataSerializer(other_category_leads, many=True)
                    paid_lead_serializer        = PaidLeadSerializers(paid_leads_pagination, many=True)
                    individual_leads_serializer = IndividualPageLeadWithoutAllDataSerializer(individual_leads_pagination, many=True)
                    viewed_lead_serializer      = BusinessPageleadViewSerializer(viewed_lead_pagination, many=True)

            except Business.DoesNotExist:
                paid_leads                 = LeadBucket.objects.filter(owner=user, is_paid=True)
                assigned_leads_per_plan    = AssignedLeadPerPremiumPlan.objects.all()
                assigned_leads_ids         = assigned_leads_per_plan.values_list('lead_id', flat=True)

                unpaid_leads               = leads.exclude(id__in=[lead_bucket.lead.id for lead_bucket in paid_leads])
                filtered_lead              = unpaid_leads.exclude(id__in=assigned_leads_ids)

                filtered_lead_pagination   = self.paginate_queryset(filtered_lead)
                paid_lead_pagination       = self.paginate_queryset(paid_leads)

                paid_lead_serializer       = UsersPaidLeadSerializer(paid_lead_pagination, many=True)
                lead_serializer            = PriceLeadWithoutAllDataSerializer(filtered_lead_pagination, many=True)

                individual_leads_serializer = None
                other_category_serializer   = None
                assigned_premium_plan_leads_serializer = None
                total_available_lead        = 0
                viewed_lead_serializer      = None

            response_data = {
                'Leads': lead_serializer.data,
                'Individual_Leads': individual_leads_serializer.data if individual_leads_serializer else [],
                'paid_leads': paid_lead_serializer.data if paid_lead_serializer else [],
                'Other_Category_Leads': other_category_serializer.data if other_category_serializer else [],
                'premium_plan_leads': [assigned_premium_plan_leads_serializer.data] if assigned_premium_plan_leads_serializer else [],
                'available_lead_view_quantity': total_available_lead,
                'plan_viewed_leads': viewed_lead_serializer.data if viewed_lead_serializer else []
            }

        else:
            all_leads = Lead.objects.all()

            try:
                if city:
                    leads = all_leads.filter(city__iexact=city, expired=False)
                elif state:
                    leads = all_leads.filter(state__iexact=state, expired=False)
                
            except Exception as e:
                return Response({'msg': 'No Lead Available in this Location'}, status=status.HTTP_204_NO_CONTENT)
            
            leads_pagination = self.paginate_queryset(leads)
            lead_serializer = PriceLeadWithoutAllDataSerializer(leads_pagination, many=True)

            response_data = {
                'Leads': lead_serializer.data
            }

        return self.get_paginated_response(response_data)




# @method_decorator(csrf_exempt)
class LeadCheckView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data

        with open('fb_lead_data.txt', 'a') as file:
            file.write(str(data) + '\n')

        return Response(status=status.HTTP_200_OK)

    def get(self, request):
        verify_token = request.GET.get('hub.verify_token')

        if verify_token == 'c8WNVaKHZaDlXbbFrltmlQtunhxT9W':
            challenge = request.GET.get('hub.challenge')
            chl       = int(challenge)

            return Response(chl, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
            # return Response("Success")
    


## This portion is used in ViewLeadData class
class ShowBusinessPageAssignedLeadView(generics.ListAPIView):
     permission_classes = [permissions.IsAuthenticated]

     def post(self, request):
        user               = request.user
        lead_id            = request.data.get('lead')
        individual_lead_id = request.data.get('individual_lead_id')
        lead_serializer    = None

        if not (lead_id or individual_lead_id):
            return Response({'msg': 'Please provide any lead to show the data'})
        
        if lead_id:
            try:
                business_page = Business.objects.get(owner=user)
                user_id       = business_page.owner

                try:
                    lead         = Lead.objects.get(id=lead_id)
                    expired_lead = lead.expired
                except Lead.DoesNotExist:
                    return Response({'msg': 'Provided lead does not exists'})

                try:
                    paid_lead = BusinessPageLeadBucket.objects.get(business_page=business_page, lead=lead, is_paid=True)
                except Exception:
                    paid_lead = None

                try:
                    viewed_lead = BusinessPageLeadView.objects.get(business_page=business_page, lead=lead, viewed=True)
                except BusinessPageLeadView.DoesNotExist:
                    viewed_lead = None

                try:
                    premium_plan_assigned_lead = AssignedLeadPerPremiumPlan.objects.get(user=user, lead=lead)
                except AssignedLeadPerPremiumPlan.DoesNotExist:
                    premium_plan_assigned_lead = None

                try:
                    available_plan      = PremiumPlanBenefits.objects.filter(user=user)
                    available_plan_lead = available_plan.aggregate(total_lead=Sum('lead_assigned'))['total_lead']
                except PremiumPlanBenefits.DoesNotExist:
                    available_plan_lead = 0

                try:
                    trial_plan = TrialPlanRequest.objects.filter(user=user, is_active=True)
                    available_trial_plan_lead = trial_plan.aggregate(total_lead=Sum('lead_view'))['total_lead']
                except TrialPlanRequest.DoesNotExist:
                    available_trial_plan_lead = 0

                total_available_lead = (available_plan_lead or 0) + (available_trial_plan_lead or 0)

                #If Purchased the lead or Expired Lead
                if expired_lead:
                    lead_serializer = LeadWithoutAllDataSerializer(lead)
                    
                elif paid_lead:
                    lead_serializer = LeadSerializer(lead)

                elif viewed_lead:
                    lead_serializer = LeadSerializer(lead)

                elif premium_plan_assigned_lead:
                    lead_serializer = LeadSerializer(lead)

                    if not BusinessPageLeadView.objects.filter(business_page=business_page, lead=lead, viewed=True).exists():
                        BusinessPageLeadView.objects.create(
                            business_page=business_page,
                            lead=lead,
                            viewed=True
                        )
                        lead.views += 1
                        lead.save()

                elif total_available_lead > 0:
                    # for benefits in available_plan:
                        if lead.category == business_page.category:
                            lead_serializer = LeadSerializer(lead)

                            if not BusinessPageLeadView.objects.filter(business_page = business_page, lead = lead, viewed=True).exists():
                                        BusinessPageLeadView.objects.create(
                                            business_page = business_page,
                                            lead          = lead,
                                            viewed        = True
                                        )
                                        lead.views += 1
                                        lead.save()

                                        if (available_trial_plan_lead or 0) > 0:
                                            for benefits in trial_plan:
                                                benefits.lead_view -= 1
                                                benefits.save()
                                                break

                                        elif (available_plan_lead or 0) > 0:
                                            for lead_benefits in available_plan:
                                                lead_benefits.lead_assigned -= 1
                                                lead_benefits.save()
                                                break 

                            # business_viewed_lead_count = BusinessPageLeadBucket.count_viewed_users(lead_id=lead)
                            # business_paid_lead_count   = BusinessPageLeadBucket.count_viewed_users(lead_id=lead)
                            # users_lead_count           = LeadBucket.count_paid_users(lead_id=lead)

                            # sum_lead_viewed = business_viewed_lead_count + users_lead_count + business_paid_lead_count

                            # if sum_lead_viewed > 10:
                            #     lead.expired = True
                            #     lead.status = 'Expired'
                            #     lead.save()
                            # break
                        else:
                            return Response({'msg': 'You can not view this category lead has to purchase the lead'})
                else:
                    return Response({'msg': 'No Available Premium Plan balance to view the lead Please Purchase'})

            except Business.DoesNotExist:
                try:
                    lead = Lead.objects.get(id=lead_id)
                    expired_lead = lead.expired
                except Lead.DoesNotExist:
                    return Response({'msg': 'Provided lead does not exists'})
                
                try:
                    paid_lead = LeadBucket.objects.get(owner=user, lead=lead, is_paid=True)
                except Exception:
                    paid_lead = None

                if paid_lead or expired_lead:
                    lead_serializer = LeadSerializer(lead)
                else:
                    return Response({'msg': 'Please purchase the lead to view the data'})

        elif individual_lead_id:
            try:
                business_page = Business.objects.get(owner=user)
                user_id       = business_page.owner

                try:
                    page_enquired_lead = BusinessPageLead.objects.get(id=individual_lead_id)
                    # expired_lead = lead.expired
                except BusinessPageLead.DoesNotExist:
                    return Response({'msg': 'Provided lead does not exists'})
                
                # try:
                #     assigned_benefits = Assigned_Benefits.objects.filter(user=user_id)
                #     lead_assigned     = [allowed_leads.assigned_lead for allowed_leads in assigned_benefits]
                # except Assigned_Benefits.DoesNotExist:
                #     lead_assigned = []
                
                try:
                    available_plan = PremiumPlanBenefits.objects.filter(user=user)
                    available_plan_lead = available_plan.aggregate(total_lead=Sum('lead_assigned'))['total_lead']
                except PremiumPlanBenefits.DoesNotExist:
                    available_plan_lead = 0

                try:
                    trial_plan = TrialPlanRequest.objects.filter(user=user, is_active=True)
                    available_trial_plan_lead = trial_plan.aggregate(total_lead=Sum('lead_view'))['total_lead']
                except TrialPlanRequest.DoesNotExist:
                    available_trial_plan_lead = 0

                total_available_lead = (available_plan_lead or 0) + (available_trial_plan_lead or 0)

                # if sum(lead_assigned) > 0:
                if total_available_lead > 0:
                    lead_serializer = IndividualLeadsSerializer(page_enquired_lead)

                    # for benefits in assigned_benefits:
                    if not BusinessPageEnquiredLeadViews.objects.filter(business_page = business_page, page_lead = page_enquired_lead, viewed=True).exists():
                                    BusinessPageEnquiredLeadViews.objects.create(
                                        business_page = business_page,
                                        page_lead      = page_enquired_lead,
                                        viewed        = True
                                    )

                                    page_enquired_lead.views += 1
                                    page_enquired_lead.save()

                                    if (available_trial_plan_lead or 0) > 0:
                                        for benefits in trial_plan:
                                            benefits.lead_view -= 1
                                            benefits.save()
                                            break

                                    elif (available_plan_lead or 0) > 0:
                                        for lead_benefits in available_plan:
                                                lead_benefits.lead_assigned -= 1
                                                lead_benefits.save()
                                                break
                else:
                    return Response({'msg': 'No Available Premium Plan balance to view the lead Please Purchase'})

            except Business.DoesNotExist:
                #Assign the brand lead to the user
                pass

        return Response({'msg': 'Lead Data Fetched Successfully', 'data': lead_serializer.data if lead_serializer else None}, status=status.HTTP_200_OK)



### View the details of a Lead
class ViewLeadData(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user               = request.user
        lead_id            = request.data.get('lead')
        individual_lead_id = request.data.get('individual_lead_id')
        lead_serializer    = None

        if not (lead_id or individual_lead_id):
            return Response({'msg': 'Please provide any lead to show the data'})

        if lead_id:
            try:
                business_page = Business.objects.get(owner=user)
                user_id      = business_page.owner

                ### Get the Lead
                try:
                    lead = Lead.objects.get(id=lead_id)
                except Lead.DoesNotExist:
                    return Response({'msg': 'Provided lead does not exists'}, status=status.HTTP_400_BAD_REQUEST)

                if lead:
                    expired_lead = lead.expired
                
                ### Get the Business page Lead view
                try:
                    viewed_lead = BusinessPageLeadView.objects.get(business_page=business_page, lead=lead, viewed=True)
                except BusinessPageLeadView.DoesNotExist:
                    viewed_lead = None

                ## Check for premium plan benefits available
                try:
                    available_plan = PremiumPlanBenefits.objects.filter(user=user)
                except PremiumPlanBenefits.DoesNotExist:
                    available_plan_lead = 0

                ## Sum the total lead quantity
                if available_plan:
                    available_plan_lead = available_plan.aggregate(total_lead=Sum('lead_assigned'))['total_lead']
                else:
                    available_plan_lead = 0

                ## Available Lead in Trial plan request
                try:
                    trial_plan = TrialPlanRequest.objects.filter(user=user, is_active=True)
                except TrialPlanRequest.DoesNotExist:
                    available_trial_plan_lead = 0
                
                ## Calculate lead available in trial plan
                if trial_plan:
                    available_trial_plan_lead = trial_plan.aggregate(total_lead=Sum('lead_view'))['total_lead']
                else:
                    available_trial_plan_lead = 0

                ## Total available lead which is the sum of trial plan and Premium plan
                total_available_lead = (available_plan_lead or 0) + (available_trial_plan_lead or 0)

                ## If the lead has been expired
                if viewed_lead:
                    lead_serializer = LeadSerializer(lead)
                  
                    # lead_serializer = LeadWithoutAllDataSerializer(lead)


                ## If the Business owner has viewed the lead
                elif expired_lead:
                    # lead_serializer = LeadSerializer(lead)
                    if viewed_lead:
                        lead_serializer = LeadSerializer(lead)
                    else:
                        lead_serializer = LeadWithoutAllDataSerializer(lead)


                # if the business owner has available lead quantity in Premium plan
                elif total_available_lead > 0:
                    if lead.category == business_page.category:
                        lead_serializer = LeadSerializer(lead)

                        if not BusinessPageLeadView.objects.filter(business_page = business_page, lead = lead, viewed=True).exists():
                            BusinessPageLeadView.objects.create(
                                business_page = business_page,
                                lead          = lead,
                                viewed        = True
                            )
                            lead.views += 1
                            lead.save()

                            if (available_trial_plan_lead or 0) > 0:
                                for benefits in trial_plan:
                                    benefits.lead_view -= 1
                                    benefits.save()
                                    break

                            elif (available_plan_lead or 0) > 0:
                                for lead_benefits in available_plan:
                                    lead_benefits.lead_assigned -= 1
                                    lead_benefits.save()
                                    break 
                                
                    else:
                        return Response({'msg': 'You can not view this category lead has to purchase the lead'}, status=status.HTTP_400_BAD_REQUEST)
                
                else:
                    return Response({'msg': 'No Available Premium Plan balance to view the lead Please Purchase'}, status=status.HTTP_400_BAD_REQUEST)
                
            except Exception as e:
                return Response({
                    'msg': 'Do not have business page'
                }, status=status.HTTP_400_BAD_REQUEST)

        ## If the Lead is Enquired to the Page
        elif individual_lead_id:
            try:
                business_page = Business.objects.get(owner=user)
                user_id       = business_page.owner

                try:
                    page_enquired_lead = BusinessPageLead.objects.get(id=individual_lead_id)
                except BusinessPageLead.DoesNotExist:
                    return Response({'msg': 'Provided lead does not exists'}, status=status.HTTP_400_BAD_REQUEST)
                
                if page_enquired_lead:
                    lead_serializer = IndividualLeadsSerializer(page_enquired_lead)

                    # for benefits in assigned_benefits:
                    if not BusinessPageEnquiredLeadViews.objects.filter(business_page = business_page, page_lead = page_enquired_lead, viewed=True).exists():
                        BusinessPageEnquiredLeadViews.objects.create(
                            business_page = business_page,
                            page_lead      = page_enquired_lead,
                            viewed        = True
                        )

                        page_enquired_lead.views += 1
                        page_enquired_lead.save()

                else:
                    return Response({'message': 'Requested Lead does not exists'}, status=status.HTTP_400_BAD_REQUEST)
                
                    
            except Exception as e:
                return Response({
                    'message': 'Invalid Business Page'
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response({'msg': 'Lead Data Fetched Successfully', 'data': lead_serializer.data if lead_serializer else None}, status=status.HTTP_200_OK)





class LeadExcelUploadView(View):
    permission_classes = [permissions.IsAdminUser]
    # parser_classes     = [MultiPartParser, FormParser]
    
    def assign_remaining_combo_lead_to_users(self, lead_id):
        balance_lead = ComboLeadBucket.objects.filter(remaining_lead__gt=0)

        try:
            lead = Lead.objects.get(id=lead_id)
        except Exception:
            return Response({'msg': 'Not able to get the lead'})

        for comboleads in balance_lead: 
            combo_lead_category = comboleads.category
            lead_category       = lead.category

            if lead_category == combo_lead_category:
                users_lead          = LeadBucket.count_paid_users(lead_id=lead)
                business_page_leads = BusinessPageLeadBucket.count_paid_users(lead_id=lead)
                all_lead_purchased  = users_lead + business_page_leads

                if all_lead_purchased >= 10:
                    lead.expired = True
                else:
                    try:
                        if business := Business.objects.get(owner=comboleads):
                            BusinessPageLeadBucket.objects.create(business_page=business, lead=lead, is_paid=True)
                    except Exception:
                        LeadBucket.objects.create(owner=comboleads.owner, lead=lead, is_paid=True)
        return {}

    def assign_premium_plan_lead_to_users(self, categories, lead_city, lead_id):
        premium_plan_users = PremiumPlanBenefits.objects.filter(
            user__business__category=categories,
            user__business__city = lead_city,
            lead_assigned__gt = 0,
            is_paid=True
        ).order_by('user')

        lead_count = 1

        for premium_plan_user in premium_plan_users:
            user = premium_plan_user.user
            lead_assigned = premium_plan_user.lead_assigned

            for _ in range(lead_assigned):
                assigned_lead = AssignedLeadPerPremiumPlan.objects.create(user=user, lead=lead_id)
                assigned_lead.save()

                premium_plan_user.lead_assigned = F('lead_assigned') - 1
                premium_plan_user.save()    

                lead_count += 1
    
       
    def post(self, request):
        form = LeadExcelUploadFrom(request.POST, request.FILES)

        drop_down_value = request.POST.get('plan')

        if not form.is_valid():
            return HttpResponse(f"Invalid Excel file {str(form.errors)}")
            # return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
        excel_file = form.cleaned_data['excel_file']

        try:
            df = pd.read_excel(excel_file)
            df.fillna('')
        except Exception as e:
            # print(f"Error during Excel parsing: {str(e)}")
            return HttpResponse(f"error: Failed to Parse the file > {str(e)}")
            # return Response({'error': 'Failed to Parse the file'}, status=status.HTTP_400_BAD_REQUEST)
        
        # total_lead_assigned_to_user = 0

        # if drop_down_value == 'all_category':
            # beat_task_to_send_lead_mail_every_10_minute.apply_async(countdown=10)

        for index,row in df.iterrows():
            try:
                lead_created_by    = row.get('Name', '')
                lead_mobile_number = row.get('Mobile Number', '')
                lead_email         = row.get('Email', '')
                lead_category      = row.get('Category', '')
                lead_state         = row.get('State', '')
                lead_city          = row.get('City', '')
                lead_pincode       = row.get('Pincode', '')
                lead_requirements  = row.get('Requirements')
            except Exception as e:
                return HttpResponse("Lead data not found")

            #Category
            categories, create = Category.objects.get_or_create(type=lead_category)

            try:
                lead_price = LeadPrice.objects.get(id=1)
            except LeadPrice.DoesNotExist:
                return HttpResponse("Create a Lead Price with ID 1")

            lead = Lead.objects.create(
                created_by    = lead_created_by,
                mobile_number = lead_mobile_number,
                email         = lead_email,
                state         = lead_state,
                city          = lead_city,
                pincode       = lead_pincode,
                category      = categories,
                requirement   = lead_requirements,
                price         = lead_price,
                status        = 'High Priority'
            )

            lead.save()

            lead_id = lead.pk

            ## Comented for some reason
            # if drop_down_value == 'all_category':
            #     business_pages = Business.objects.filter(category=categories, city=lead_city)

            #     beat_task_to_send_lead_mail_every_10_minute.apply_async(countdown=20)

            if drop_down_value == 'W/O_Premium_Plan':
                # premium_plan = PremiumPlanBenefits.objects.filter(is_paid=True)

                business_pages = Business.objects.filter(city=lead_city, category=categories)

                # business_pages = businesses.exclude(owner__in=premium_plan.values('user'))

                # Create User from Lead data
                try:
                    user, created = User.objects.get_or_create(
                        mobile_number = lead_mobile_number
                    )

                    if created:
                        user.name = lead_created_by
                        user.save()

                        user_data = [{
                        'customer_name': lead_created_by,
                        'lead_id': lead.pk, 
                        'mobile_number': lead_mobile_number,
                        'category': categories.type,
                        }]
                        send_whatsapp_message_enqiury_form_user.delay(user_data)

                except Exception as e:
                    pass


                data = [
                    {
                        'business_email': business.email,
                        'business_name': business.business_name,
                        'location': lead_city, 
                        'customer_name': lead_created_by,
                        'requirements': lead_requirements, 
                        'mobile_number': business.mobile_number
                    }
                    for business in business_pages
                ]

                try:
                    send_category_wise_business_whatsapp_message_lead_excel_upload.delay(data)
                except Exception as e:
                    return HttpResponse(f"Not able to sent mail {str(e)}")
                
                # try:
                #     send_category_wise_business_mail_excel_upload.delay(data)
                # except Exception as e:
                #     return HttpResponse(f"Not able to sent mail {str(e)}")

                try:
                    send_category_wise_business_message_excel_upload.delay(data)
                except Exception as e:
                    return HttpResponse(f"Not able to sent mail {str(e)}")
                

            elif drop_down_value == 'combo_lead':
                combo_lead = ComboLead.objects.all()
                
                businesses = Business.objects.filter(city=lead_city, category=categories)

                business_pages = businesses.filter(owner__in=combo_lead.values('user'))

                self.assign_remaining_combo_lead_to_users(lead_id)

                data = [
                    {
                        'business_email': business.email,
                        'business_name': business.business_name,
                        'location': lead_city, 
                        'customer_name': lead_created_by,
                        'requirements': lead_requirements, 
                        'mobile_number': business.mobile_number
                    }
                    for business in business_pages
                ]

               
                # try:
                #     send_category_wise_business_mail_excel_upload.delay(data)
                # except Exception as e:
                #     return HttpResponse(f"Not able to sent mail {str(e)}")

                try:
                    send_category_wise_business_message_excel_upload.delay(data)
                except Exception as e:
                    return HttpResponse(f"Not able to sent mail {str(e)}")
                
            else:
                # user_premium_plan = PremiumPlanBenefits.objects.filter(is_paid=True)

                business_pages = Business.objects.filter(city=lead_city, category=categories)

                # business_pages = businesses.filter(owner__in=user_premium_plan.values('user'))
                
                # self.assign_premium_plan_lead_to_users(categories, lead_city, lead_id)
                

                # Create User from Lead data
                try:
                    user, created = User.objects.get_or_create(
                        mobile_number = lead_mobile_number
                    )

                    if created:
                        user.name = lead_created_by
                        user.save()

                        user_data = [{
                        'customer_name': lead_created_by,
                        'lead_id': lead.pk, 
                        'mobile_number': lead_mobile_number,
                        'category': categories.type,
                        }]

                        send_whatsapp_message_enqiury_form_user.delay(user_data)

                except Exception as e:
                    pass

                # try:
                #     send_category_wise_business_mail_excel_upload.delay(data)
                # except Exception as e:
                #     return HttpResponse(f"Not able to sent mail {str(e)}")
                data = [
                {
                    'business_email': business.email,
                    'business_name': business.business_name,
                    'location': lead_city, 
                    'customer_name': lead_created_by,
                    'requirements': lead_requirements, 
                    'mobile_number': business.mobile_number,
                }
                for business in business_pages
                ]

                try:
                    send_category_wise_business_whatsapp_message_lead_excel_upload.delay(data)
                except Exception as e:
                    return HttpResponse(f"Not able to sent mail {str(e)}")

                try:
                    send_category_wise_business_message_excel_upload.delay(data)
                except Exception as e:
                    return HttpResponse(f"Not able to sent mail {str(e)}")
                

            response_data = {'msg': 'Mail has been sent to the user'}

        return render(request, 'Admin/lead_excel_upload.html', response_data)
    
    def get(self, request):
        return render(request, 'Admin/lead_excel_upload.html')




class ComboLeadPaymentInitiationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ComboLeadPaymentSerializer(data=request.data)

        if serializer.is_valid():
            amount         = serializer.validated_data.get('amount')
            phonepe_amount = amount * 100
            current_user   = request.user
            combo_category = request.data.get("category")
            cities         = request.data.get("cities", [])
            combo_lead_id  = request.data.get('combo_lead_id')

            try:
                order = ComboLeadOrder.objects.create(user=current_user, amount=amount)
                transaction_id = order.transaction_id

                payment_response = ComboLeadPaymentInitiation(transaction_id, phonepe_amount, combo_category, cities, combo_lead_id)
                return Response({'msg': 'Payment initiation successful', 'payment_response': payment_response},
                                status=status.HTTP_200_OK)

            except ComboLeadOrder.DoesNotExist:
                return Response({'msg': 'Lead order does not get created'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            
        else:
            response = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "bad request",
                "error": serializer.errors
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST) 



@method_decorator(csrf_exempt, name='dispatch')
class ComboLeadPaymentCompleteView(View):
    # permission_classes = [permissions.IsAuthenticated]

    def less_available_lead_for_user(self, available_leads_value, combo_lead_quantity, user, actual_lead_to_assign):
        assign_lead = available_leads_value

        remaining_lead_quantity = combo_lead_quantity - available_leads_value
        email = user.email

        for lead_to_assign in actual_lead_to_assign[:assign_lead]:

            users_lead          = LeadBucket.count_paid_users(lead_id=lead_to_assign)
            business_page_leads = BusinessPageLeadBucket.count_paid_users(lead_id=lead_to_assign)
            all_lead_purchased  = users_lead + business_page_leads

            if all_lead_purchased >= 10:
                lead_status = Lead.objects.get(id=lead_to_assign.pk)
                lead_status.expired = True
            else:
                LeadBucket.objects.create(
                    owner=user, lead=lead_to_assign, is_paid=True
                    )

        data = {
            'email': email,
            'remaining_lead': remaining_lead_quantity
        }

        # send_mail_for_remaining_combo_lead.delay(data)


    def less_available_lead_for_business_page(self, user, available_leads_value, combo_lead_quantity, actual_lead_to_assign):
        business_page = Business.objects.get(owner=user.id)

        assign_quantity         = available_leads_value
        remaining_lead_quantity = combo_lead_quantity - available_leads_value

        email = business_page.email

        for lead in actual_lead_to_assign[:assign_quantity]:

            users_lead          = LeadBucket.count_paid_users(lead_id=lead)
            business_page_leads = BusinessPageLeadBucket.count_paid_users(lead_id=lead)
            all_lead_purchased  = users_lead + business_page_leads

            if all_lead_purchased >= 10:
                lead_status = Lead.objects.get(id=lead.pk)
                lead_status.expired = True
            else:
                BusinessPageLeadBucket.objects.create(
                    business_page=business_page, lead = lead, is_paid=True
                    )

        data = {
            'email': email,
            'remaining_lead': remaining_lead_quantity
        }

        send_mail_for_remaining_combo_lead.delay(data)


    def post(self, request):
        INDEX        = "1"
        SALTKEY      = config("SALT_KEY")

        #Phonepe Response
        payment_status = request.POST.get('code', None)
        merchant_id = request.POST.get('merchantId', None)
        transaction_id = request.POST.get('transactionId', None)
        check_sum = request.POST.get('checksum', None)
        provider_reference_id = request.POST.get('providerReferenceId', None)
        merchant_order_id = request.POST.get('merchantOrderId', None)

        #Query Params
        combo_lead_id  = request.GET.get('combo_id')
        combo_category = request.GET.get('combo_category')
        cities         = request.GET.get('cities', [])

        if transaction_id:
            request_url = 'https://api.phonepe.com/apis/hermes/status/FBM225/' + transaction_id
            sha256_Pay_load_String = '/pg/v1/status/FBM225/' + transaction_id + SALTKEY
            sha256_val = calculate_sha256_string(sha256_Pay_load_String)
            checksum = sha256_val + '###' + INDEX

            headers = {
            'Content-Type': 'application/json',
            'X-VERIFY': checksum,
            'X-MERCHANT-ID': transaction_id,
            }

            response = requests.get(request_url, headers=headers)

            try:
                order = ComboLeadOrder.objects.get(transaction_id=transaction_id)
            except ComboLeadOrder.DoesNotExist:
                response_data = {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Client Order with the specified provider_order_id not found",
                    }
                return redirect("https://www.famousbusiness.in/")
            
            order.provider_reference_id = provider_reference_id
            order.merchant_id           = merchant_id
            order.checksum              = check_sum
            order.status                = payment_status
            order.isPaid                = True
            order.details               = f'Purchased a Combo Lead of of ID'
            order.message               = response.text
            order.merchant_order_id     = merchant_order_id
            user                        = order.user
            order.save()

            if payment_status == "PAYMENT_SUCCESS":
                try:
                    combo_lead = ComboLead.objects.get(id=combo_lead_id)
                except ComboLead.DoesNotExist:
                    return redirect("https://www.famousbusiness.in/")
                
                try:
                    category = Category.objects.get(id=combo_category)
                except Category.DoesNotExist:
                    return redirect("https://www.famousbusiness.in/?not_category=True")

                try:
                    ComboLeadBucket.objects.create(owner=user, combolead_id=combo_lead.pk, category=category, is_paid=True)
                except ComboLeadBucket.DoesNotExist:
                    return redirect("https://www.famousbusiness.in/?not_combolead=True")
                
                #Process TO Assign leads to users
                #Available_leads = Lead.objects.filter(category=combo_category, expired=False)

                available_leads = []
                for city in cities:
                    city_wise_lead = Lead.objects.filter(category=combo_category, expired=False, city=city)
                    available_leads.extend(city_wise_lead)

                #Exclude the leads which are the Business owner has already purchased
                with contextlib.suppress(Exception):
                    business              = Business.objects.get(owner=user.id)
                    existing_lead         = BusinessPageLeadBucket.objects.filter(business_page=business).values_list('lead', flat=True)
                    actual_lead_to_assign = [lead for lead in available_leads if lead.id not in existing_lead]
                    available_leads_value = len(actual_lead_to_assign)
                
                #Remove the leads which are the users has already purchased
                try:
                    existing_lead         = LeadBucket.objects.filter(owner=user.id).values_list('lead', flat=True)

                    actual_lead_to_assign = [lead for lead in available_leads if lead.id not in existing_lead]
                    available_leads_value = len(actual_lead_to_assign)
                except Exception:
                    actual_lead_to_assign = available_leads
                    available_leads_value = len(actual_lead_to_assign)
                
                combo_lead          = ComboLead.objects.get(id=combo_lead_id)
                combo_lead_quantity = combo_lead.lead_quantity

                if available_leads_value < combo_lead_quantity:
                    try:
                        self.less_available_lead_for_business_page(
                            user,
                            available_leads_value,
                            combo_lead_quantity,
                            actual_lead_to_assign,
                        )
                    except Business.DoesNotExist:
                        self.less_available_lead_for_user(
                            available_leads_value,
                            combo_lead_quantity,
                            user,
                            actual_lead_to_assign,
                        )
       
                elif available_leads_value > combo_lead_quantity:   
                    try:
                        business_page = Business.objects.get(owner=user.id)

                        assign_quantity = combo_lead_quantity

                        for lead in actual_lead_to_assign[:assign_quantity]:
                            
                            users_lead          = LeadBucket.count_paid_users(lead_id=lead)
                            business_page_leads = BusinessPageLeadBucket.count_paid_users(lead_id=lead)
                            all_lead_purchased  = users_lead + business_page_leads

                            if all_lead_purchased >= 10:
                                lead_status = Lead.objects.get(id=lead_to_assign)
                                lead_status.expired = True
                            else:
                                BusinessPageLeadBucket.objects.create(
                                    business_page=business_page, lead = lead, is_paid=True
                                    )
       
                    except Business.DoesNotExist:
                        assign_lead = combo_lead_quantity

                        for lead_to_assign in actual_lead_to_assign[:assign_lead]:

                            users_lead          = LeadBucket.count_paid_users(lead_id=lead_to_assign)
                            business_page_leads = BusinessPageLeadBucket.count_paid_users(lead_id=lead_to_assign)
                            all_lead_purchased  = users_lead + business_page_leads

                            if all_lead_purchased >= 10:
                                lead_status = Lead.objects.get(id=lead_to_assign)
                                lead_status.expired = True
                            else:
                                LeadBucket.objects.create(owner=user, lead=lead_to_assign, is_paid=True)

                    # return Response({'msg': 'Lead has been added to your bucket Please check in your Paid Leads'})

                # response_data = {
                #     "status_code": status.HTTP_201_CREATED,
                #     "message": "Transaction created"
                # }
                return redirect("https://www.famousbusiness.in/success")
            else:
                return redirect("https://www.famousbusiness.in/failure")
            # return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return redirect("https://www.famousbusiness.in/failure")

        
    



#Use in Combo Lead Payment Complete time
class ComboLeadCheckAfterPaymentCompleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def less_available_lead_for_user(self, available_leads_value, combo_lead_quantity, user, actual_lead_to_assign):
        assign_lead = available_leads_value

        remaining_lead_quantity = combo_lead_quantity - available_leads_value
        email = user.email

        for lead_to_assign in actual_lead_to_assign[:assign_lead]:

            users_lead          = LeadBucket.count_paid_users(lead_id=lead_to_assign)
            business_page_leads = BusinessPageLeadBucket.count_paid_users(lead_id=lead_to_assign)
            all_lead_purchased  = users_lead + business_page_leads

            if all_lead_purchased >= 10:
                lead_status = Lead.objects.get(id=lead_to_assign.pk)
                lead_status.expired = True
            else:
                LeadBucket.objects.create(
                    owner=user, lead=lead_to_assign, is_paid=True
                    )

        data = {
            'email': email,
            'remaining_lead': remaining_lead_quantity
        }

        # send_mail_for_remaining_combo_lead.delay(data)

    def less_available_lead_for_business_page(self, user, available_leads_value, combo_lead_quantity, actual_lead_to_assign):
        business_page = Business.objects.get(owner=user.id)

        assign_quantity         = available_leads_value
        remaining_lead_quantity = combo_lead_quantity - available_leads_value

        email = business_page.email

        for lead in actual_lead_to_assign[:assign_quantity]:

            users_lead          = LeadBucket.count_paid_users(lead_id=lead)
            business_page_leads = BusinessPageLeadBucket.count_paid_users(lead_id=lead)
            all_lead_purchased  = users_lead + business_page_leads

            if all_lead_purchased >= 10:
                lead_status = Lead.objects.get(id=lead.pk)
                lead_status.expired = True
            else:
                BusinessPageLeadBucket.objects.create(
                    business_page=business_page, lead = lead, is_paid=True
                    )

        data = {
            'email': email,
            'remaining_lead': remaining_lead_quantity
        }

        # send_mail_for_remaining_combo_lead.delay(data)



    def post(self, request): 
        lead_category = request.data.get('lead_category')
        user          = request.user
        combo_lead_id = request.data.get('combo_lead_id')
        # city          = request.data.get('city')
        cities        = request.data.get('cities', []) 

        available_leads = []
        for city in cities:
            city_wise_lead = Lead.objects.filter(category=lead_category, expired=False, city=city)
            available_leads.extend(city_wise_lead)

        # available_leads = Lead.objects.filter(category=lead_category, expired=False, city=city)
        # print(len(available_leads))
       
        #Exclude the leads which are the Business owner has already purchased
        with contextlib.suppress(Exception):
            business              = Business.objects.get(owner=user.id)
            existing_lead         = BusinessPageLeadBucket.objects.filter(business_page=business).values_list('lead', flat=True)
            actual_lead_to_assign = [lead for lead in available_leads if lead.id not in existing_lead]
            available_leads_value = len(actual_lead_to_assign)

        #Remove the leads which are the users has already purchased
        try:
            existing_lead         = LeadBucket.objects.filter(owner=user.id).values_list('lead', flat=True)

            actual_lead_to_assign = [lead for lead in available_leads if lead.id not in existing_lead]
            available_leads_value = len(actual_lead_to_assign)
        except Exception:
            actual_lead_to_assign = available_leads
            available_leads_value = len(available_leads)

        combo_lead          = ComboLead.objects.get(id=combo_lead_id)
        combo_lead_quantity = combo_lead.lead_quantity

        if available_leads_value < combo_lead_quantity:
            try:
                self.less_available_lead_for_business_page(
                    user,
                    available_leads_value,
                    combo_lead_quantity,
                    actual_lead_to_assign,
                )
            except Business.DoesNotExist:
                self.less_available_lead_for_user(
                    available_leads_value,
                    combo_lead_quantity,
                    user,
                    actual_lead_to_assign,
                )

        elif available_leads_value > combo_lead_quantity:   
            try:
                business_page = Business.objects.get(owner=user.id)
                assign_quantity = combo_lead_quantity

                for lead in actual_lead_to_assign[:assign_quantity]:

                    users_lead          = LeadBucket.count_paid_users(lead_id=lead)
                    business_page_leads = BusinessPageLeadBucket.count_paid_users(lead_id=lead)
                    all_lead_purchased  = users_lead + business_page_leads

                    if all_lead_purchased >= 10:
                        lead_status = Lead.objects.get(id=lead_to_assign)
                        lead_status.expired = True
                    else:
                        BusinessPageLeadBucket.objects.create(
                            business_page=business_page, lead = lead, is_paid=True
                            )

            except Business.DoesNotExist:
                assign_lead = combo_lead_quantity

                for lead_to_assign in actual_lead_to_assign[:assign_lead]:
                    users_lead          = LeadBucket.count_paid_users(lead_id=lead_to_assign)
                    business_page_leads = BusinessPageLeadBucket.count_paid_users(lead_id=lead_to_assign)
                    all_lead_purchased  = users_lead + business_page_leads

                    if all_lead_purchased >= 10:
                        lead_status = Lead.objects.get(id=lead_to_assign)
                        lead_status.expired = True
                    else:
                        LeadBucket.objects.create(owner=user, lead=lead_to_assign, is_paid=True)

        return Response({'msg': 'Lead has been added to your bucket Please check in your Paid Leads'})




class IDWiseComboLeadView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class   =  ComboLeadSerializer

    def get(self, request, combo_id):
        combo_lead_id = combo_id

        combo_lead = ComboLead.objects.get(id = combo_lead_id)
        
        serializer = self.get_serializer(combo_lead)

        return Response({'msg': 'Data Fetched Successfully', 'data': serializer.data})
        
    



### Get all the details of a lead form category wise
class LeadFormDetails(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        lead_form_category = request.data.get("category")

        ## Get the category
        try:
            get_category = Category.objects.get(type=lead_form_category)
        except Exception as e:
            return Response({'message': 'Invalid Category'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            category_lead_form  = LeadFrorm.objects.get(category = get_category)
        except Exception as e:
            return Response({
                'message': 'Lead Form not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = GetLeadFormSerializer(category_lead_form)

        return Response({
            'success': True,
            'lead_form_data': serializer.data
            }, status=status.HTTP_200_OK)
    


### Generate Lead from Lead form
class LeadGenerateFromLeadForm(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        full_name    = request.data.get('full_name')
        phone_number = request.data.get('mobile_number')
        category_name = request.data.get('category')

        ## Category
        try:
            category_obj = Category.objects.get(type = category_name)
        except Exception as e:
            return Response({'message': 'Invalid Category'}, status=status.HTTP_400_BAD_REQUEST)
        

        ## Generate Lead
        try:
            new_lead = Lead.objects.create(
                created_by    = full_name,
                category      = category_obj,
                mobile_number = phone_number,
                state         = 'Not updated',
                city          = 'Not Updated',
                status        = 'Open'
            )

            return Response({
                'message': 'Lead generated successfully',
                'success': True,
                'lead_id': new_lead.pk

                }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'message': 'Lead not generated'}, status=status.HTTP_400_BAD_REQUEST)


### Update Lead with Lead form Questions
class LeadFormUpdateQuestionView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        requirements = request.data.get('requirements')
        state        = request.data.get('city')
        city         = request.data.get('state')
        lead_id      = request.data.get('lead_id')

        ## get the lead
        try:
            Lead_obj = Lead.objects.get(id = lead_id)
        except Exception as e:
            return Response({'message': 'Invalid Lead'}, status=status.HTTP_400_BAD_REQUEST)
            
        Lead_obj.requirement = requirements

        if city and state:
            Lead_obj.city        = city
            Lead_obj.state       = state

            Lead_obj.save()

        else:
            try:
                lead_form_obj   = LeadFrorm.objects.get(category = Lead_obj.category)
                Lead_obj.city   = lead_form_obj.city
                Lead_obj.state  = lead_form_obj.state

            except Exception as e:
                pass

            Lead_obj.save()

        return Response({'message': 'Lead updated Successfully'}, status=status.HTTP_200_OK)
    




### Get all the Lead Banner data according to state, city and Category
class LeadBannerView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        state    = request.query_params.get("state")
        city     = request.query_params.get('city')
        user     = request.user

        # Get the Business pag
        try:
            business_page = Business.objects.get(owner = user)
        except Exception as e:
            return Response({'message': "Business page does not exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        ### Get the category
        try:
            category_obj = Category.objects.get(type = business_page.category)
        except Exception as e:
            return Response({'message': 'Invalid Category'}, status=status.HTTP_400_BAD_REQUEST)


        if category_obj:
            ## get the banner related to the category
            try:
                lead_banners = LeadBanner.objects.filter(
                    category = category_obj,
                    city     = city
                )
            except Exception as e:
                return Response({'message': f'Lead banner not found {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
            
            if lead_banners.exists():
                serializer = LeadBannerSerializer(lead_banners, many=True)
            else:
                serializer = None

        else:
            serializer = None


        return Response({
            'success': True,
            'lead_banner_data': serializer.data if serializer else None

        }, status=status.HTTP_200_OK)

