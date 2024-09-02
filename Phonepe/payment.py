from decouple import config
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import json
import base64
import uuid
import requests
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view






def calculate_sha256_string(input_string):
    sha256 = hashes.Hash(hashes.SHA256(), backend=default_backend())
    sha256.update(input_string.encode('utf-8'))
    return sha256.finalize().hex()




def base64_encode(input_dict):
    json_data = json.dumps(input_dict)
    data_bytes = json_data.encode('utf-8')
    return base64.b64encode(data_bytes).decode('utf-8')




def pay(request):
    transaction_id = str(uuid.uuid4())
    
    MAINPAYLOAD = {
        "merchantId": config("MERCHANT_ID"),
        "merchantTransactionId": transaction_id,
        "merchantUserId": config("MERCHANT_USER_ID"),
        "amount": 100,
        "redirectUrl": "http://127.0.0.1:8000/message-api/return-to-me/?lead_id=5",
        "redirectMode": "POST",
        "callbackUrl": "http://127.0.0.1:8000/message-api/return-to-me/",
        "mobileNumber": "8249258412",
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
def payment_return(request):
    INDEX = "1"
    SALTKEY = "083f0f7b-217c-4930-a6ba-49f6140376da"
    form_data = request.POST
    form_data_dict = dict(form_data)

    transaction_id = form_data.get('transactionId', None)

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

    return render(request, 'index.html', {'output': response.text, 'main_request': form_data_dict})



