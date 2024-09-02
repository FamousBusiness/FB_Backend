from decouple import config
from Phonepe.payment import base64_encode, calculate_sha256_string
import requests






def SoftwarePaymentInitiation(transaction_id, amount, name):

    MAINPAYLOAD = {
        "merchantId": config("MERCHANT_ID"),
        "merchantTransactionId": transaction_id,
        "merchantUserId": config("MERCHANT_USER_ID"),
        "amount": amount,
        "redirectUrl": f"https://api.famousbusiness.in/soft-api/payment-complete/?name={name}",
        "redirectMode": "POST",
        "callbackUrl": f"https://api.famousbusiness.in/soft-api/payment-complete/?name={name}",
        "mobileNumber": "9883835373",
        "paymentInstrument": {
            "type": "PAY_PAGE"
        }
    }

    INDEX = "1"
    ENDPOINT = "/pg/v1/pay"
    SALTKEY = config("SALT_KEY")
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

    response = {
        'redirect_url': responseData['data']['instrumentResponse']['redirectInfo']['url'],
    }

    return response