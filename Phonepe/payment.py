from decouple import config
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import json
import base64
import uuid
import requests
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt






def calculate_sha256_string(input_string):
    sha256 = hashes.Hash(hashes.SHA256(), backend=default_backend())
    sha256.update(input_string.encode('utf-8'))
    return sha256.finalize().hex()




def base64_encode(input_dict):
    json_data = json.dumps(input_dict)
    data_bytes = json_data.encode('utf-8')
    return base64.b64encode(data_bytes).decode('utf-8')


Merchant_Id = ''
Merchant_User_Id = ''
Salt_key    = ''
api_url     = ''
webhook_url = ''
redirect_url = ''


Is_development = config("IS_DEVELOPMENT")



if Is_development == 'True':
    Merchant_Id      = config('PHONEPE_TEST_MERCHANT_ID')
    Salt_key         = config('PHONEPE_TEST_SALT_KEY')
    Merchant_User_Id = config('MERCHANT_USER_ID')
    api_url          = config('PHONEPE_SANDBOX_URL')
    webhook_url      = 'http://127.0.0.1:8000'
    redirect_url     = 'http://localhost:3000'

else:
    # Merchant_Id      = config("MERCHANT_ID")
    Merchant_Id      = config('PHONEPE_TEST_MERCHANT_ID')
    # Salt_key         = config('SALT_KEY')
    Salt_key         = config('PHONEPE_TEST_SALT_KEY')
    Merchant_User_Id = config('MERCHANT_USER_ID')
    # api_url          = config('PHONEPE_PRODUCTION_URL')
    api_url          = config('PHONEPE_SANDBOX_URL')
    webhook_url      = 'https://api.famousbusiness.in'
    redirect_url     = 'https://store.famousbusiness.in'



def PhonepayPayment(amount, transaction_id):
    
    MAINPAYLOAD = {
        "merchantId": Merchant_Id,
        "merchantTransactionId": transaction_id,
        "merchantUserId": Merchant_User_Id,
        "amount": int(amount),
        "redirectUrl": f"{redirect_url}/payment/success",
        "redirectMode": "REDIRECT",
        "callbackUrl": f"{webhook_url}/api/ecom/v1/phonepe/payment/response/",
        "mobileNumber": "8598039147",
        "paymentInstrument": {
            "type": "PAY_PAGE"
        }
    }

    INDEX = "1"
    ENDPOINT = "/pg/v1/pay"
    SALTKEY = f"{Salt_key}"
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

    response = requests.post(f'{api_url}', headers=headers, json=json_data)

    response.raise_for_status()
    responseData = response.json()

    return responseData['data']['instrumentResponse']['redirectInfo']['url']





@csrf_exempt
def payment_return(request):
    INDEX = "1"
    SALTKEY = Salt_key
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



