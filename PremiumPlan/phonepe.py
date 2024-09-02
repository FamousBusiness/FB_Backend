from decouple import config
from Phonepe.payment import base64_encode, calculate_sha256_string
import requests







def PremiumPlanPaymentInitiation(transaction_id, amount, plan_id):
   
    MAINPAYLOAD = {
        "merchantId": config("MERCHANT_ID"),
        "merchantTransactionId": transaction_id,
        "merchantUserId": config("MERCHANT_USER_ID"),
        "amount": amount,
        "redirectUrl": f"https://api.famousbusiness.in/premium-plan-api/premium-plan-payment-complete/?plan_id={plan_id}",
        "redirectMode": "POST",
        "callbackUrl": f"https://api.famousbusiness.in/premium-plan-api/premium-plan-payment-complete/?plan_id={plan_id}",
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