from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView
from Listings.models import Business
from PremiumPlan.phonepe import PremiumPlanPaymentInitiation
from .models import (PremiumPlan, PlanCancelRequest, TrialPlanRequest,
                     PremiumPlanOrder, PremiumPlanBenefits)
from .serializers import (
    PremiumPlanSerializer, PremiumPlanPaymentSerializer,
    PremiumPlanDashboardSerializer
    )
from django.conf import settings
from Listings.RazorpayPayment.razorpay.main import RazorpayClient
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from Listings.constants import PaymentStatus
from .permissions import IsAdminuserOrReadOnly, IsAdminuserOrAllReadOnly
from .tasks import premium_plan_purchase_mail, send_trial_plan_activation_mail, send_trial_plan_request_mail_to_admin
from users.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from decouple import config
import requests
from Phonepe.payment import calculate_sha256_string




CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)
rz_client = RazorpayClient()



class AllPremiumPlanView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):

        monthly_premium_plan = PremiumPlan.objects.filter(plan__duration='Monthly')
        yearly_premium_plan  = PremiumPlan.objects.filter(plan__duration='Yearly')
        trial_plan           = PremiumPlan.objects.filter(plan__duration='Day')

        monthly_serializer    = PremiumPlanSerializer(monthly_premium_plan, many=True)
        yearly_serializer     = PremiumPlanSerializer(yearly_premium_plan, many=True)
        trial_plan_serializer = PremiumPlanSerializer(trial_plan, many=True)
       
        response = {
            'Monthly': monthly_serializer.data,
            'Yearly': yearly_serializer.data,
            'Trial_Plan': trial_plan_serializer.data
        }
        # print(monthly_serializer.data)
        return Response({'status': 'Success', 'data': response}, status=status.HTTP_200_OK)





class PremiumPlanPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PremiumPlanPaymentSerializer(data=request.data)

        if serializer.is_valid():
            received_amount = serializer.validated_data.get('amount')
            amount          = received_amount * 100
            current_user    = request.user
            plan_id         = request.data.get('premium_plan_id')

            try:
                premium_plan_instance = PremiumPlan.objects.get(id=plan_id)
            except PremiumPlan.DoesNotExist:
                return Response({'msg': 'Premium Plan Does Not exists'})
            
            try:
                order            = PremiumPlanOrder.objects.create( amount=received_amount, user=current_user,
                                                    details=f'Purchased {premium_plan_instance.plan.name} {premium_plan_instance.plan.type}' )
                transaction_id   = order.transaction_id
                payment_response = PremiumPlanPaymentInitiation(transaction_id, amount, plan_id)

                return Response({'msg': 'Payment initiation successful', 'payment_response': payment_response},
                                status=status.HTTP_200_OK)
            except PremiumPlanOrder.DoesNotExist:
                return Response({'msg': 'Unable to Create the Order'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        else:
            response = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "bad request",
                "error": serializer.errors
            }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)



#Get The Business ID and According to the Premium plan benefits create those in Business ID
@method_decorator(csrf_exempt, name='dispatch')
class PremiumPlanPaymentCompleteView(View):
    # permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        INDEX        = "1"
        SALTKEY      = config("SALT_KEY")

        #Phonepe Response
        payment_status        = request.POST.get('code', None)
        merchant_id           = request.POST.get('merchantId', None)
        transaction_id        = request.POST.get('transactionId', None)
        check_sum             = request.POST.get('checksum', None)
        provider_reference_id = request.POST.get('providerReferenceId', None)
        merchant_order_id     = request.POST.get('merchantOrderId', None)

        #Query Params
        plan_id = request.GET.get('plan_id')
        
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
                order = PremiumPlanOrder.objects.get(transaction_id=transaction_id)
            except PremiumPlanOrder.DoesNotExist:
                return redirect("https://www.famousbusiness.in/")
            
            try:
                plan_instance = PremiumPlan.objects.get(id=plan_id)
            except PremiumPlan.DoesNotExist:
                return redirect("https://www.famousbusiness.in/?no_plan=True")
            

            order.provider_reference_id = provider_reference_id
            order.merchant_id           = merchant_id
            order.checksum              = check_sum
            order.status                = payment_status
            order.isPaid                = True
            order.details               = f'Purchased plan: {plan_instance}'
            order.message               = response.text
            order.merchant_order_id     = merchant_order_id
            user                        = order.user
            order.save()

            if payment_status == "PAYMENT_SUCCESS":

                try:
                    business_instance = Business.objects.get(owner=user)
                except Exception as e:
                    return redirect("https://www.famousbusiness.in/?no_business=True")

                data = {
                    'business_mail': business_instance.email,
                    'transaction_id': transaction_id,
                    'business_name': business_instance.business_name,
                    'amount': order.amount
                }

                try:
                    plan_benefits, created = PremiumPlanBenefits.objects.get_or_create(user=order.user, plan=plan_instance, is_paid=True)
                except PremiumPlanBenefits.DoesNotExist:
                    return redirect("https://www.famousbusiness.in/?no_benefits=True")

                try:
                    previous_available_lead     = plan_benefits.lead_assigned
                    premiumplan_lead_value      = plan_instance.lead_view
                    total_lead_view             = previous_available_lead + premiumplan_lead_value

                    previous_available_job_post = plan_benefits.jobpost_allowed
                    premiumplan_jobpost_value   = plan_instance.job_post
                    total_jobpost_value         = previous_available_job_post + premiumplan_jobpost_value

                    plan_benefits.lead_assigned   = total_lead_view
                    plan_benefits.jobpost_allowed = total_jobpost_value

                    business_instance.verified        = plan_instance.verified
                    business_instance.trusted         = plan_instance.trusted 
                    business_instance.trending        = plan_instance.trending
                    business_instance.authorized      = plan_instance.authorized
                    business_instance.sponsor         = plan_instance.sponsor
                    business_instance.super           = plan_instance.super
                    business_instance.premium         = plan_instance.premium
                    business_instance.industry_leader = plan_instance.industry_leader
                    
                    business_instance.save()
                    plan_benefits.save()

                    premium_plan_purchase_mail.delay(data)

                except Business.DoesNotExist:
                    return Response({'msg': 'Business does not get Updated'})

                response = {
                    "status_code": status.HTTP_201_CREATED,
                    "message": "Transaction created"
                }

                return redirect("https://www.famousbusiness.in/success")
            else:
                return redirect("https://www.famousbusiness.in/failure")
        else:
            return redirect("https://www.famousbusiness.in/failure")
    


##Only Admin can access to POST and PUT
class PremiumPlanAPIView(APIView):
    permission_classes = [IsAdminuserOrReadOnly]
    
    def get(self, request):
        premium_plan = PremiumPlan.objects.all()
        serializer = PremiumPlanSerializer(premium_plan, many=True)
        return Response({'status': 'Success', 'data': serializer.data}, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = PremiumPlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'msg': 'Data Saved Successfully'}, status=status.HTTP_200_OK)


    def put(self, request, plan_id):
        try:
            plan = PremiumPlan.objects.get(id=plan_id)
        except:
            return Response({'mag': 'No plan exist'})
        
        serializer = PremiumPlanSerializer(plan, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'msg': 'Data Saved Succefully'}, status=status.HTTP_201_CREATED)
    



class CancelPlanView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, plan):
        user    = request.user
        plan_id = plan

        try:
            premium_plan = PremiumPlan.objects.get(id=plan_id)
        except PremiumPlan.DoesNotExist:
            return Response({'msg': 'Premium Plan Does not exists'})
        
        PlanCancelRequest.objects.create(
            user = user,
            plan = premium_plan
        )

        return Response({'msg': 'Cancel Request raised Successfully'}, status=status.HTTP_200_OK)
   

# from Listings.permissions import CustomeTokenPermission
class PremiumPlanPerUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        # print(request.COOKIES.get('access'))

        try:
            user_plan = PremiumPlanBenefits.objects.filter(user=user)
        except PremiumPlanBenefits.DoesNotExist:
            return Response({'msg': 'No Plan Available'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PremiumPlanDashboardSerializer(user_plan, many=True)
        
        return Response({'msg': 'Plan data fetched successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
    




class TrialPlanActivationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        plan_id    = request.data.get('premium_plan_id')
        
        try:
            premium_plan = PremiumPlan.objects.get(id=plan_id)
        except PremiumPlan.DoesNotExist:
            return Response({'msg': 'Premium plan does not exist'})
        
        trial_plan, created = TrialPlanRequest.objects.get_or_create(user=user, plan=premium_plan, lead_view=premium_plan.lead_view)
        
        if trial_plan:
            if trial_plan.is_active:
                return Response({'msg': 'Already Purchased the Plan'}, status=status.HTTP_403_FORBIDDEN)
            else:
                data = {
                    'user_name': user.name,
                }
                send_trial_plan_request_mail_to_admin.delay(data)
        else:
            TrialPlanRequest.objects.create(
                user=user, 
                plan=premium_plan, 
                lead_view=premium_plan.lead_view
                )

        return Response({'msg': 'Request Raised you will be notify after activation'})
    




class TrialPlanAdminApprovalView(View):
    def get(self, request, *args, **kwargs):
        trial_plan = TrialPlanRequest.objects.all()

        data = {
            'trial_plan': trial_plan
        }
        return render(request, 'PremiumPlan/trial_plan.html', data)

    def post(self, request, *args, **kwargs):
        status = request.POST.get('status')
        business_name = request.POST.get('business_name')

        try:
            registered_business = Business.objects.get(business_name=business_name)
        except User.DoesNotExist:
            return HttpResponse("Not Registered User")
        
        trial_plan = TrialPlanRequest.objects.get(user=registered_business.owner)

        if status == 'True':
            trial_plan.is_active = True
            registered_business.industry_leader = trial_plan.plan.industry_leader
            registered_business.verified        = trial_plan.plan.verified
            registered_business.trusted         = trial_plan.plan.trusted
            registered_business.trending        = trial_plan.plan.trending
            registered_business.authorized      = trial_plan.plan.authorized
            registered_business.sponsor         = trial_plan.plan.sponsor
            registered_business.super           = trial_plan.plan.super
            registered_business.premium         = trial_plan.plan.premium

            registered_business.save()

            data = {
                'business_mail': registered_business.email,
                'lead_view_quantity': trial_plan.lead_view,
                'business_name': registered_business.business_name
            }
            send_trial_plan_activation_mail.delay(data)

        else:
            trial_plan.is_active = False

            registered_business.industry_leader = False
            registered_business.verified        = False
            registered_business.trusted         = False
            registered_business.trending        = False
            registered_business.authorized      = False
            registered_business.sponsor         = False
            registered_business.super           = False
            registered_business.premium         = False

            registered_business.save()
            
        trial_plan.save()

        return HttpResponse('Submitted Successfully')    