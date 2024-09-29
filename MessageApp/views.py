from django.utils import timezone
from django.views import View
import pandas as pd
from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
import requests
#Payment Imports
import json
import base64
import requests
import uuid
from django.shortcuts import render, redirect
from django.http import HttpResponse
from cryptography.hazmat.primitives import hashes
from django.views.decorators.csrf import csrf_exempt
from cryptography.hazmat.backends import default_backend
from Admin.forms import AdminExcelUploadForm
from Lead.models import Lead, LeadOrder
from Listings.models import Business, Category
from users.models import User
from django.db.models import Q








class SendTESTSMSView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        # serializer = SMSSerializer(data=request.data)
        # if serializer.is_valid():

        #     sms_data = serializer.validated_data
        url = "http://trans.smsfresh.co/api/sendmsg.php"

        params = {
            "user": 'WEBZOTICAPROMO',
            "pass": '123456',
            "sender": 'WBFSPL',
            "phone": '8249258412',
            "text": 'New%20Lead%20has%20been%20assign%20for%20your%20Business.%0A%20Please%20Share%20the%20Quotation.%0A%20Regards%2C%20WFBSPL%20famousbusiness.in%0A%209871475373',
            "priority": 'ndnd',
            "stype": 'normal'
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            return Response({"message": "API request successful", "response": response.text}, status=status.HTTP_200_OK)
        else:
            return Response({"message": f"API request failed with status code {response.status_code}", "response": response.text}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # else:
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



def calculate_sha256_string(input_string):
    sha256 = hashes.Hash(hashes.SHA256(), backend=default_backend())
    sha256.update(input_string.encode('utf-8'))
    return sha256.finalize().hex()



def base64_encode(input_dict):
    json_data = json.dumps(input_dict)
    data_bytes = json_data.encode('utf-8')
    return base64.b64encode(data_bytes).decode('utf-8')



def index(request):
    return render(request, "index.html", { 'output': "Please Pay & Repond From The Payment Gateway Will Come In This Section", 'main_request': "" })




def pay(request):
    transaction_id = str(uuid.uuid4())
    
    MAINPAYLOAD = {
        "merchantId": "M22BWNC10OPNQ",
        "merchantTransactionId": transaction_id,
        "merchantUserId": "FBM225",
        "amount": 100,
        # "redirectUrl": "http://127.0.0.1:8000/message-api/payment-successfull/",
        "redirectUrl": f"http://127.0.0.1:8000/message-api/return-to-me/?lead_id={5}/",
        "redirectMode": "POST",
        # "callbackUrl": "http://127.0.0.1:8000/message-api/payment-successfull/",
        "callbackUrl": f"http://127.0.0.1:8000/message-api/return-to-me/?lead_id={5}/",
        "mobileNumber": "9883835373",
        "paymentInstrument": {
            "type": "PAY_PAGE"
        }
    }

    INDEX = "1"
    ENDPOINT = "/pg/v1/pay"
    SALTKEY = "083f0f7b-217c-4930-a6ba-49f6140376da"
    base64String = base64_encode(MAINPAYLOAD)
    mainString = base64String + ENDPOINT + SALTKEY
    sha256Val = calculate_sha256_string(mainString)
    checkSum = sha256Val + '###' + INDEX

    headers = {
        'Content-Type': 'application/json',
        'X-VERIFY': checkSum,
        'accept': 'application/json',
    }

    json_data = {
        'request': base64String,
    }

    response = requests.post('https://api.phonepe.com/apis/hermes/pg/v1/pay', headers=headers, json=json_data)

    response.raise_for_status()
    responseData = response.json()
    return redirect(responseData['data']['instrumentResponse']['redirectInfo']['url'])





@csrf_exempt
def Payment_Successfull(request):
    form_data = request.POST
    print(form_data)
    return HttpResponse("Success")



# @csrf_exempt
# def payment_return(request):
#     INDEX = "1"
#     SALTKEY = "083f0f7b-217c-4930-a6ba-49f6140376da"
#     form_data = request.POST
#     print(form_data)
#     print(form_data.get('code'))
#     form_data_dict = dict(form_data)

#     print('Hii')
#     transaction_id = form_data.get('transactionId', None)

#     if transaction_id:
#         request_url = 'https://api.phonepe.com/apis/hermes/status/FBM225/' + transaction_id
#         sha256_Pay_load_String = '/pg/v1/status/FBM225/' + transaction_id + SALTKEY
#         sha256_val = calculate_sha256_string(sha256_Pay_load_String)
#         checksum = sha256_val + '###' + INDEX

#         headers = {
#             'Content-Type': 'application/json',
#             'X-VERIFY': checksum,
#             'X-MERCHANT-ID': transaction_id,
#         }

#         response = requests.get(request_url, headers=headers)
#     else:
#         lead = Lead.objects.create(created_by='Naresh')

#     return HttpResponse()

    # return render(request, 'index.html', {'output': response.text, 'main_request': form_data_dict})






# @api_view(['POST'])
# @permission_classes([AllowAny])
@csrf_exempt
def payment_return(request):
    INDEX = "1"
    SALTKEY = "083f0f7b-217c-4930-a6ba-49f6140376da"
   
    form_data = request.POST
    lead_id = request.GET.get("lead_id")
    status  = form_data.get('code')
    # print(status)
    form_data_dict = dict(form_data)

    # print(form_data)
    # print(f"POST Data:{form_data}")
    # print(f"Lead: {lead_id}")

    transaction_id = form_data.get('transactionId', None)
    merchant_id    = form_data.get("merchantId", None)
    lead_id        = request.GET.get('lead_id')
        

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

        if status == "PAYMENT_SUCCESS":
            return redirect('https://www.famousbusiness.in/success') 
        else:
            return redirect("https://www.famousbusiness.in/failure")

    return redirect("https://www.famousbusiness.in/leads")
    # return render(request, 'index.html', {'output': response.text, 'main_request': form_data_dict})



# class LeadCheck(generics.ListAPIView):
#     permission_classes = [permissions.AllowAny]
#     # pagination_class   = PageNumberPagination

#     def post(self, request):
#         current_date = timezone.now().date()
#         current_month = current_date.month
#         current_year  = current_date.year

#         leads = Lead.objects.filter(
#         created_at__date=current_date, 
#         created_at__month=current_month,
#         created_at__year=current_year,
#         mail_sent=False)

#         for lead in leads:
#             business_pages = Business.objects.filter(category=lead.category, city=lead.city)
            
#             for business in business_pages:
#                 print(business)
                
#             break
        
#         return Response({'msg': 'Success'})
    

class LeadCheck(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        order = LeadOrder.objects.get(user_id=29)
        # print(order.user.pk)
        try:
            business = Business.objects.get(owner=order.user)

            if business:
                print(business)
        except Exception as e:
            return Response("No Business page found")
        return Response("Done")
    



# @method_decorator
class SendWhatsAppTestMessage(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        api_url = "https://trans.smsfresh.co/api/sendmsg.php"
        business_name = "Ranjit"
        category = "Interior"
        Email    = "ranjit@mail.com"

        params = {
        "user" : "WEBZOTICA",
        "pass" : "123456",
        "sender" : "BUZWAP",
        "phone" : "8249258412",
        "text": "final_001",
        "priority" : "wa",
        "stype" : "normal",
        "Params": "1,2,3",
        "htype" : "image",
        "imageUrl" : "https://mdwebzotica.famousbusiness.in/lead_uplaod_img.jpg"
        }

        url = f"{api_url}?user={params['user']}&pass={params['pass']}&sender={params['sender']}&phone={params['phone']}&text={params['text']}&priority={params['priority']}&stype={params['stype']}&htype={params['htype']}&url={params['imageUrl']}"
 
        response = requests.get(url, params=params)

        # print(response)
        if response.status_code == 200:
            return Response("Message sent Successfully")
        else:
            return Response("Unable to send Whatsapp Message")
        
        

