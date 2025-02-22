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
from Admin.models import AutoPaySuccessResponse
from .serializers import (
    PremiumPlanSerializer, PremiumPlanPaymentSerializer,
    PremiumPlanDashboardSerializer
)
from django.conf import settings
from Listings.RazorpayPayment.razorpay.main import RazorpayClient
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from Listings.constants import PaymentStatus
from .permissions import IsAdminuserOrReadOnly
from .tasks import premium_plan_purchase_mail, send_trial_plan_activation_mail, send_trial_plan_request_mail_to_admin, send_premium_plan_first_invoice
from users.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from decouple import config
import requests
from Phonepe.payment import calculate_sha256_string
from Phonepe.encoded import base64_decode
from PremiumPlan.models import PhonepeAutoPayOrder
from Phonepe.autopay import PremiumPlanPhonepeAutoPayPayment, PhoenepePennyDropAutopay
from django.utils import timezone
from PremiumPlan.generate_pdf import generate_pdf


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)
rz_client = RazorpayClient()


class AllPremiumPlanView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        try:
            existing_business = Business.objects.get(owner = user)
        except Exception as e:
            return Response({'message': 'No plan available for user'}, status=status.HTTP_404_NOT_FOUND)
        

        try:
            monthly_premium_plan = PremiumPlan.objects.filter(plan__duration='Monthly', category = existing_business.category)

            if not monthly_premium_plan:
                monthly_premium_plan = []

        except Exception as e:
            monthly_premium_plan = []

        try:
            yearly_premium_plan  = PremiumPlan.objects.filter(plan__duration='Yearly', category = existing_business.category)

            if not yearly_premium_plan:
                yearly_premium_plan = []

        except Exception as e:
            yearly_premium_plan = []
        
        try:
            trial_plan = PremiumPlan.objects.filter(autopay_payment_type='One Month Free', category = existing_business.category)

            if not trial_plan:
                trial_plan = []
                
        except Exception as e:
            trial_plan = []

        
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


# Premium plan payment
class PremiumPlanPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PremiumPlanPaymentSerializer(data=request.data)

        if serializer.is_valid():
            received_amount = serializer.validated_data.get('amount')
            amount = received_amount
            current_user = request.user
            plan_id = request.data.get('premium_plan_id')

            try:
                premium_plan_instance = PremiumPlan.objects.get(id=plan_id)
            except PremiumPlan.DoesNotExist:
                return Response({'msg': 'Premium Plan Does Not exists'})

            # Create Phonepe Order
            phonePeOrder = PhonepeAutoPayOrder.objects.create(
                amount=amount,
                premium_plan_id=premium_plan_instance,
                user_id=current_user
            )

            # Create user subscription step
            if premium_plan_instance.autopay_payment_type:
                if premium_plan_instance.autopay_payment_type == 'Paid':
                    # 1st step Create user subscription
                    try:
                        create_user = PremiumPlanPhonepeAutoPayPayment.Create_user_Subscription(
                            phonePeOrder.MerchantSubscriptionId, phonePeOrder.merchantUserId, phonePeOrder.amount)
                    except Exception as e:
                        return Response({'message': f'{str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

                elif premium_plan_instance.autopay_payment_type == 'One Month Free':
                    # 1st step Create user subscription
                    try:
                        create_user = PhoenepePennyDropAutopay.Create_user_Subscription(
                            phonePeOrder.MerchantSubscriptionId, phonePeOrder.amount)
                    except Exception as e:
                        return Response({'message': f'{str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

            else:
                # 1st step Create user subscription
                try:
                    create_user = PremiumPlanPhonepeAutoPayPayment.Create_user_Subscription(
                        phonePeOrder.MerchantSubscriptionId, phonePeOrder.merchantUserId, phonePeOrder.amount)
                except Exception as e:
                    return Response({'message': f'{str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

            # Create user subscription step Ends here

            subscriptionID = create_user['data']['subscriptionId']

            if subscriptionID:
                # Update Phonepe order with Subscription ID
                phonePeOrder.subscriptionId = subscriptionID
                phonePeOrder.save()

                authRequestID = phonePeOrder.authRequestId
                order_amount = phonePeOrder.amount

                ###################################
                # SubmitAuth QR Request Starts Here
                ###################################
                if premium_plan_instance.autopay_payment_type:
                    if premium_plan_instance.autopay_payment_type == 'Paid':
                        try:
                            # 2nd step Submit QR Auth Request
                            create_qr_subscription_auth_request = PremiumPlanPhonepeAutoPayPayment.SubmitAuthRequestQR(
                                subscriptionID, order_amount, authRequestID
                            )
                        except Exception as e:
                            return Response({'message': f'{str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

                    elif premium_plan_instance.autopay_payment_type == 'One Month Free':
                        try:
                            # 2nd step Submit QR Auth Request
                            create_qr_subscription_auth_request = PhoenepePennyDropAutopay.SubmitAuthRequestQR(
                                subscriptionID, authRequestID
                            )
                        except Exception as e:
                            return Response({'message': f'{str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

                else:
                    try:
                        # 2nd step Submit QR Auth Request
                        create_qr_subscription_auth_request = PremiumPlanPhonepeAutoPayPayment.SubmitAuthRequestQR(
                            subscriptionID, order_amount, authRequestID
                        )
                    except Exception as e:
                        return Response({'message': f'{str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

                ################################
                # SUBMITAUTH REQUEST ENDS HERE
                #################################

                QRCOde = create_qr_subscription_auth_request['data']['redirectUrl']

                return Response({
                    'message': 'Success',
                    'QR_Code': QRCOde,
                    'authRequestId': phonePeOrder.authRequestId
                },

                    status=status.HTTP_200_OK)

            else:
                return Response({'message': 'Error occures'}, status=status.HTTP_400_BAD_REQUEST)

        else:
            response = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "bad request",
                "error": serializer.errors
            }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)


# Pay through UPI ID
class PaythorughUPIID(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        current_user = request.user
        upi_id = request.data.get('upi_id')
        amount = request.data.get('amount')
        plan_id = request.data.get('premium_plan_id')

        try:
            premium_plan_instance = PremiumPlan.objects.get(id=plan_id)
        except PremiumPlan.DoesNotExist:
            return Response({'msg': 'Premium Plan Does Not exists'})

        # Create Phonepe Order
        phonePeOrder = PhonepeAutoPayOrder.objects.create(
            amount=amount,
            premium_plan_id=premium_plan_instance,
            user_id=current_user
        )

        #########################################
        # Create user subscription starts here
        ###########################################
        if premium_plan_instance.autopay_payment_type:
            if premium_plan_instance.autopay_payment_type == 'Paid':
                # 1st step Create user subscription
                try:
                    create_user = PremiumPlanPhonepeAutoPayPayment.Create_user_Subscription(
                        phonePeOrder.MerchantSubscriptionId, phonePeOrder.merchantUserId, phonePeOrder.amount)
                except Exception as e:
                    return Response({'message': f'{str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

            elif premium_plan_instance.autopay_payment_type == 'One Month Free':
                # 1st step Create user subscription
                try:
                    create_user = PhoenepePennyDropAutopay.Create_user_Subscription(
                        phonePeOrder.MerchantSubscriptionId, phonePeOrder.amount)
                except Exception as e:
                    return Response({'message': f'{str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                create_user = PremiumPlanPhonepeAutoPayPayment.Create_user_Subscription(
                    phonePeOrder.MerchantSubscriptionId, phonePeOrder.merchantUserId, phonePeOrder.amount)
            except Exception as e:
                return Response({'message': f'{str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        #######################################
        # Create user Subscription ends here
        ########################################
        subscriptionID = create_user['data']['subscriptionId']

        if subscriptionID:
            # Update Phonepe order with Subscription ID
            phonePeOrder.subscriptionId = subscriptionID
            phonePeOrder.save()

            authRequestID = phonePeOrder.authRequestId
            order_amount = phonePeOrder.amount

            ######################################
            # SubmitAuth Request Starts here
            ########################################
            if premium_plan_instance.autopay_payment_type:
                if premium_plan_instance.autopay_payment_type == 'Paid':
                    try:
                        submit_auth_reuqest = PremiumPlanPhonepeAutoPayPayment.SubmitAuthRequestUPICollect(
                            subscriptionID, order_amount,
                            authRequestID, upi_id
                        )
                    except Exception as e:
                        return Response({'message': f"{str(e)}"}, 400)

                elif premium_plan_instance.autopay_payment_type == 'One Month Free':
                    try:
                        # 2nd step Submit QR Auth Request
                        submit_auth_reuqest = PhoenepePennyDropAutopay.SubmitAuthRequestUPICollect(
                            subscriptionID, authRequestID, upi_id
                        )
                    except Exception as e:
                        return Response({'message': f'{str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                try:
                    submit_auth_reuqest = PremiumPlanPhonepeAutoPayPayment.SubmitAuthRequestUPICollect(
                        subscriptionID, order_amount,
                        authRequestID, upi_id
                    )
                except Exception as e:
                    return Response({'message': f"{str(e)}"}, 400)

            ############################################
            # SubmiAuth Request Ends Here
            #############################################
            if submit_auth_reuqest['success'] == True:
                return Response({
                    'success': True,
                    'authRequestId': phonePeOrder.authRequestId
                }, status=status.HTTP_200_OK)

            else:
                return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({'msessage': 'Phonepe order does not exist'}, status=status.HTTP_400_BAD_REQUEST)


# Receive AutopayWebhook from Phonepe after First payment
@method_decorator(csrf_exempt, name='dispatch')
class ReceivePhonepeAutoPayWebhook(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        response_data = request.data.get('response')
        # Decode the response
        decoded_data = base64_decode(response_data)

        if decoded_data['success'] == True and decoded_data['data']['transactionDetails']['state'] == 'COMPLETED' and decoded_data['data']['subscriptionDetails']['state'] == 'ACTIVE':

            authRequestID = decoded_data['data']['authRequestId']
            subscriptionID = decoded_data['data']['subscriptionDetails']['subscriptionId']

            # Get the related Phonepe order
            auto_pay_order = PhonepeAutoPayOrder.objects.get(
                authRequestId=authRequestID,
                subscriptionId=subscriptionID
            )

            if auto_pay_order:
                # Get the premium plan ID related to order
                premium_plan = auto_pay_order.premium_plan_id

                # Get the premium plan
                # premium_plan = PremiumPlan.objects.get(
                #     id = premium_plan_id
                # )

                # Get the user
                # user_obj = User.objects.get(
                #     id = auto_pay_order.user_id
                # )
                user_obj = auto_pay_order.user_id

                order, created = PremiumPlanOrder.objects.get_or_create(
                    user=user_obj,
                    premium_plan=premium_plan
                )

                if created:
                    order.transaction_id = auto_pay_order.authRequestId
                    order.amount = auto_pay_order.amount
                    order.status = 'Paid'
                    order.details = f'Purchased Premium plan - {premium_plan.plan.name} {premium_plan.plan.type}'
                    order.isPaid = True

                    order.save()

                else:
                    order.transaction_id = auto_pay_order.authRequestId
                    order.amount = auto_pay_order.amount
                    order.status = 'Paid'
                    order.details = f'Purchased Premium plan - {premium_plan.plan.name} {premium_plan.plan.type}'
                    order.isPaid = True

                    order.save()

                try:
                    business_instance = Business.objects.get(owner=user_obj)

                    if business_instance:
                        # Send Invoice to the Business
                        try:
                            generate_pdf(user_obj, order)
                        except Exception as e:
                            pass

                        try:
                            data = {
                                'mobile_number': business_instance.mobile_number,
                                'document_name': str(order.invoice)
                            }
                            send_premium_plan_first_invoice.apply_async(
                                args=[data], countdown=5)

                        except Exception as e:
                            pass

                except Exception as e:
                    order.details = f'Amount paid but unable to get the business, user name - {user_obj.name}, user iD - {user_obj.pk}'
                    order.save()
                    return Response({'success': True}, status=status.HTTP_200_OK)

                try:
                    plan_benefits, created = PremiumPlanBenefits.objects.get_or_create(
                        user=order.user, plan=premium_plan, is_paid=True)
                except Exception as e:
                    order.details = f'Amount paid but unable to Assign the benefits, user name - {user_obj.name}, user iD - {user_obj.pk}'
                    order.save()

                    return Response({'success': True}, status=status.HTTP_200_OK)

                try:
                    previous_available_lead = plan_benefits.lead_assigned
                    premiumplan_lead_value = premium_plan.lead_view
                    total_lead_view = previous_available_lead + premiumplan_lead_value

                    previous_available_job_post = plan_benefits.jobpost_allowed
                    premiumplan_jobpost_value = premium_plan.job_post
                    total_jobpost_value = previous_available_job_post + premiumplan_jobpost_value

                    plan_benefits.lead_assigned = total_lead_view
                    plan_benefits.jobpost_allowed = total_jobpost_value

                    business_instance.verified = premium_plan.verified
                    business_instance.trusted = premium_plan.trusted
                    business_instance.trending = premium_plan.trending
                    business_instance.authorized = premium_plan.authorized
                    business_instance.sponsor = premium_plan.sponsor
                    business_instance.super = premium_plan.super
                    business_instance.premium = premium_plan.premium
                    business_instance.industry_leader = premium_plan.industry_leader

                    business_instance.save()
                    plan_benefits.save()

                    # premium_plan_purchase_mail.delay(data)

                except Exception as e:
                    order.details = f'Amount paid but unable to Assign all the benefits, user name - {user_obj.name}, user iD - {user_obj.pk}'
                    order.save()

                    return Response({'success': True}, status=status.HTTP_200_OK)

                return Response({'success': True}, status=status.HTTP_200_OK)

        return Response({"message": "Success"}, status=status.HTTP_200_OK)


# Payment Status of Autopayment
class AutoPayPaymentStatusCheck(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        authRequestId = request.data.get('authRequestId')

        # Get the phonepe order with merchant User Id
        try:
            auto_pay_order = PhonepeAutoPayOrder.objects.get(
                authRequestId=authRequestId
            )
        except Exception as e:
            return Response({'message': 'Did not found autopay order'}, status=status.HTTP_400_BAD_REQUEST)

        if auto_pay_order:
            check_payment_status = PremiumPlanPhonepeAutoPayPayment.CheckPaymentStatus(
                auto_pay_order.authRequestId
            )

            if check_payment_status['success'] == True and check_payment_status['message'] == 'Your subscription is active':
                return Response({'message': 'Status is now active'}, status=status.HTTP_200_OK)

            elif check_payment_status['success'] == True and check_payment_status['data']['transactionDetails']['state'] == 'PENDING':
                return Response({'message': "Transaction is pending"}, status=status.HTTP_201_CREATED)

            return Response({'success': True}, status=status.HTTP_302_FOUND)

        else:
            return Response({'message': 'Did not found autopay order'}, status=status.HTTP_400_BAD_REQUEST)


# Deduct Periodic Amount
class RecurringInitPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):

        try:
            orders_to_deduct = PremiumPlanOrder.objects.all()
        except Exception as e:
            return Response({'message': 'Premium plan does not exists'}, status=status.HTTP_400_BAD_REQUEST)

        current_date = timezone.now()

        for order in orders_to_deduct:
            days_since_purchase = (current_date - order.purchased_at).days

            if days_since_purchase == 29:
                transactionID = order.transaction_id
                phonepe_order = PhonepeAutoPayOrder.objects.get(
                    authRequestId=transactionID)

                try:
                    recurring_payment = PremiumPlanPhonepeAutoPayPayment.RecurringInit(
                        phonepe_order.subscriptionId,
                        phonepe_order.merchantUserId,
                        phonepe_order.amount,
                        phonepe_order.authRequestId
                    )

                except Exception as e:
                    return Response({'message': f'{str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Recurring payment deducted successfully'}, status=status.HTTP_200_OK)


# Webhook Response for Recurring payment
class RecurringPaymentWebhook(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # get the payload data from phonepe
        payload_data = request.data
        response = payload_data['response']

        # Decode the response
        try:
            decoded_payload = base64_decode(response)
        except Exception as e:
            return Response({"message": "Error decoding payload", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if not decoded_payload:
            return Response({"message": "Invalid decoded payload"}, status=status.HTTP_400_BAD_REQUEST)

        # Get the transaction ID
        subscriptionID = decoded_payload['data']['subscriptionDetails']['subscriptionId']

        try:
            phonepe_order = PhonepeAutoPayOrder.objects.get(
                subscriptionId=subscriptionID)
            phonepe_order.webhook_response = str(decoded_payload)

            success = False
            message = ''

            if decoded_payload['message'] and decoded_payload['message'] == 'Payment Failed':
                success = False
                message = 'Not able to deduct the payment'

            elif decoded_payload['message'] and decoded_payload['message'] == 'Your payment is successful':
                success = True
                message = 'Payment Deducted Successfully'

            else:
                success = False
                message = 'Not able to deduct the payment'

            try:
                premium_plan_order = PremiumPlanOrder.objects.get(
                    transaction_id=phonepe_order.authRequestId,
                    user=phonepe_order.user_id
                )

                # IF the plan has been Paused then deactivate the order
                if premium_plan_order and decoded_payload['data']['subscriptionDetails']['state'] == 'PAUSED':
                    premium_plan_order.is_active = False
                    premium_plan_order.save()

                elif premium_plan_order and decoded_payload['data']['subscriptionDetails']['state'] == 'REVOKED':
                    premium_plan_order.is_active = False
                    premium_plan_order.save()

            except Exception as e:
                pass
                # return Response({"message": 'Invalid Premium Plan'}, status=status.HTTP_400_BAD_REQUEST)

            # Register the Succcess Response for the User
            auto_pay_success_response = AutoPaySuccessResponse(
                user=phonepe_order.user_id,
                transaction_id=phonepe_order.recurring_transaction_id,
                premium_plan=phonepe_order.premium_plan_id,
                phonepe_response=str(decoded_payload),
                subscriptionID=phonepe_order.subscriptionId,
                is_success=success,
                message=message,
                status=decoded_payload['data']['subscriptionDetails']['state']
            )

            phonepe_order.save()
            auto_pay_success_response.save()

        except Exception as e:
            return Response({'message': 'Not able to get the order'}, status=status.HTTP_400_BAD_REQUEST)

        if decoded_payload['data']['notificationDetails']['state'] == 'NOTIFIED' and decoded_payload['data']['subscriptionDetails']['state'] == 'ACTIVE' and decoded_payload['data']['transactionDetails']['state'] == 'COMPLETED':
            # Assign Premium Plan benefits to the user
            try:
                premium_plan_order = PremiumPlanOrder.objects.get(
                    transaction_id=phonepe_order.authRequestId,
                    user=phonepe_order.user_id
                )
            except Exception as e:
                return Response({"message": 'Invalid Premium Plan'}, status=status.HTTP_400_BAD_REQUEST)

            # Generate PDF for the user
            try:
                generate_pdf(phonepe_order.user_id, premium_plan_order)
            except Exception as e:
                pass

            # Send Invpoice In Whatsapp to user
            try:
                business_instance = Business.objects.get(
                    owner=phonepe_order.user_id)

                data = {
                    'mobile_number': business_instance.mobile_number,
                    'document_name': str(premium_plan_order.invoice)
                }
                send_premium_plan_first_invoice.apply_async(
                    args=[data], countdown=5)

            except Exception as e:
                pass

            premium_plan_order.webhook_response = str(decoded_payload)
            premium_plan_order.month_paid = (
                premium_plan_order.month_paid or 0) + 1
            premium_plan_order.repayment_date = timezone.now()
            premium_plan_order.status = 'Paid'
            premium_plan_order.request_sent = False
            premium_plan_order.save()

            # Get the premium plan ID related to order
            premium_plan_id = phonepe_order.premium_plan_id

            try:
                premium_plan = PremiumPlan.objects.get(pk=premium_plan_id)
            except Exception as e:
                return Response({'message': 'Invalid Plan'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                premium_plan_benefit = PremiumPlanBenefits.objects.get(
                    user=premium_plan_order.user, plan=premium_plan_id)

                # Get the premium plan related to the benefit
                premium_plan_lead_quantity = premium_plan_benefit.plan.lead_view
                premium_plan_benefit.lead_assigned = premium_plan_lead_quantity

                premium_plan_benefit.save()

            except Exception as e:
                pass
                # return Response({'message': 'Invalid Plan Benefit'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'success': True}, status=status.HTTP_200_OK)

        return Response({'success': True}, status=status.HTTP_200_OK)


# Cancel the Plan
class CancelAutopayPayment(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        user_id = user.id

        # Get the Premiumplan Order of the user
        user_premiumplan_order = PremiumPlanOrder.objects.get(
            user=user
        )
        return Response({'message': "In Progress"}, 200)


# Get The Business ID and According to the Premium plan benefits create those in Business ID
@method_decorator(csrf_exempt, name='dispatch')
class PremiumPlanPaymentCompleteView(View):

    def post(self, request):
        INDEX = "1"
        SALTKEY = config("SALT_KEY")

        # Phonepe Response
        payment_status = request.POST.get('code', None)
        # merchant_id           = request.POST.get('merchantId', None)
        transaction_id = request.POST.get('transactionId', None)
        # check_sum             = request.POST.get('checksum', None)
        # provider_reference_id = request.POST.get('providerReferenceId', None)
        # merchant_order_id     = request.POST.get('merchantOrderId', None)

        # Query Params
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
                order = PremiumPlanOrder.objects.get(
                    transaction_id=transaction_id)
            except PremiumPlanOrder.DoesNotExist:
                return redirect("https://www.famousbusiness.in/")

            try:
                plan_instance = PremiumPlan.objects.get(id=plan_id)
            except PremiumPlan.DoesNotExist:
                return redirect("https://www.famousbusiness.in/?no_plan=True")

            # order.provider_reference_id = provider_reference_id
            # order.merchant_id           = merchant_id
            # order.checksum              = check_sum
            order.status = payment_status
            order.isPaid = True
            order.details = f'Purchased plan: {plan_instance}'
            # order.message               = response.text
            # order.merchant_order_id     = merchant_order_id
            user = order.user
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
                    plan_benefits, created = PremiumPlanBenefits.objects.get_or_create(
                        user=order.user, plan=plan_instance, is_paid=True)
                except PremiumPlanBenefits.DoesNotExist:
                    return redirect("https://www.famousbusiness.in/?no_benefits=True")

                try:
                    previous_available_lead = plan_benefits.lead_assigned
                    premiumplan_lead_value = plan_instance.lead_view
                    total_lead_view = previous_available_lead + premiumplan_lead_value

                    previous_available_job_post = plan_benefits.jobpost_allowed
                    premiumplan_jobpost_value = plan_instance.job_post
                    total_jobpost_value = previous_available_job_post + premiumplan_jobpost_value

                    plan_benefits.lead_assigned = total_lead_view
                    plan_benefits.jobpost_allowed = total_jobpost_value

                    business_instance.verified = plan_instance.verified
                    business_instance.trusted = plan_instance.trusted
                    business_instance.trending = plan_instance.trending
                    business_instance.authorized = plan_instance.authorized
                    business_instance.sponsor = plan_instance.sponsor
                    business_instance.super = plan_instance.super
                    business_instance.premium = plan_instance.premium
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


# Only Admin can access to POST and PUT
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
        user = request.user
        plan_id = plan

        try:
            premium_plan = PremiumPlan.objects.get(id=plan_id)
        except PremiumPlan.DoesNotExist:
            return Response({'msg': 'Premium Plan Does not exists'})

        PlanCancelRequest.objects.create(
            user=user,
            plan=premium_plan
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
        plan_id = request.data.get('premium_plan_id')

        try:
            premium_plan = PremiumPlan.objects.get(id=plan_id)
        except PremiumPlan.DoesNotExist:
            return Response({'msg': 'Premium plan does not exist'})

        trial_plan, created = TrialPlanRequest.objects.get_or_create(
            user=user, plan=premium_plan, lead_view=premium_plan.lead_view)

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
            registered_business = Business.objects.get(
                business_name=business_name)
        except User.DoesNotExist:
            return HttpResponse("Not Registered User")

        trial_plan = TrialPlanRequest.objects.get(
            user=registered_business.owner)

        if status == 'True':
            trial_plan.is_active = True
            registered_business.industry_leader = trial_plan.plan.industry_leader
            registered_business.verified = trial_plan.plan.verified
            registered_business.trusted = trial_plan.plan.trusted
            registered_business.trending = trial_plan.plan.trending
            registered_business.authorized = trial_plan.plan.authorized
            registered_business.sponsor = trial_plan.plan.sponsor
            registered_business.super = trial_plan.plan.super
            registered_business.premium = trial_plan.plan.premium

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
            registered_business.verified = False
            registered_business.trusted = False
            registered_business.trending = False
            registered_business.authorized = False
            registered_business.sponsor = False
            registered_business.super = False
            registered_business.premium = False

            registered_business.save()

        trial_plan.save()

        return HttpResponse('Submitted Successfully')
