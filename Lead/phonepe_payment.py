import requests
from decouple import config
from Phonepe.payment import base64_encode, calculate_sha256_string





def LeadPaymentInitiation(transaction_id, amount, lead_instance_id):
    lead_id = lead_instance_id
    MAINPAYLOAD = {
        "merchantId": config("MERCHANT_ID"),
        "merchantTransactionId": transaction_id,
        "merchantUserId": config("MERCHANT_USER_ID"),
        "amount": amount,
        "redirectUrl": f"https://api.famousbusiness.in/lead-api/lead-payment-complete/?lead={lead_id}",
        "redirectMode": "POST",
        "callbackUrl": f"https://api.famousbusiness.in/lead-api/lead-payment-complete/?lead={lead_id}",
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




def ComboLeadPaymentInitiation(transaction_id, phonepe_amount, combo_category, cities, combo_lead_id):
 
    MAINPAYLOAD = {
        "merchantId": config("MERCHANT_ID"),
        "merchantTransactionId": transaction_id,
        "merchantUserId": config("MERCHANT_USER_ID"),
        "amount": phonepe_amount,

        "redirectUrl": f"https://api.famousbusiness.in/lead-api/combo-lead-payment-complete/?combo_id={combo_lead_id}&combo_category={combo_category}&cities={cities}",

        "redirectMode": "POST",

        "callbackUrl": f"https://api.famousbusiness.in/lead-api/combo-lead-payment-complete/?combo_id={combo_lead_id}&combo_category={combo_category}&cities={cities}",

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

