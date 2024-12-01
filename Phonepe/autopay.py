from Phonepe.encoded import base64_encode, calculate_sha256_string
from decouple import config
import requests
from decouple import config



IS_DEVELOPMENT = config('IS_DEVELOPMENT')

if IS_DEVELOPMENT == 'True':
    webhook_url    = 'https://1e50-2405-204-1389-91d5-e1dc-29cb-3441-de61.ngrok-free.app/premium-plan-api/autopay/payment/webhook/'
    TestMerchantId = config('PHONEPE_TEST_MERCHANT_ID')
    merchantID     = config('MERCHANT_ID')
    TestsaltKey    = config('PHONEPE_TEST_SALT_KEY') # test key
    SaltKey        = config('SALT_KEY')
    TestURl        = 'https://api-preprod.phonepe.com/apis/pg-sandbox'
    prodURL        = 'https://mercury-t2.phonepe.com'
else:
    webhook_url    = 'https://api.famousbusiness.in/premium-plan-api/autopay/payment/webhook/'
    TestMerchantId = config('PHONEPE_TEST_MERCHANT_ID')
    merchantID     = config('MERCHANT_ID')
    TestsaltKey    = config('PHONEPE_TEST_SALT_KEY') # test key
    SaltKey        = config('SALT_KEY')
    TestURl        = 'https://api-preprod.phonepe.com/apis/pg-sandbox'
    prodURL        = 'https://mercury-t2.phonepe.com'




# Phonepe Autopay
class PremiumPlanPhonepeAutoPayPayment:

    # Create User Subscription API
    def Create_user_Subscription(subscriptionID, userID, amount):
        sent_amount = amount * 100

        payload = {
            "merchantId": merchantID,
            "merchantSubscriptionId": subscriptionID,
            "merchantUserId": "FVSGHHSB3456AFFS89876GH",
            "authWorkflowType": "TRANSACTION",
            "amountType": "VARIABLE",
            # "amountType": "FIXED",
            "amount": sent_amount ,
            "frequency": "MONTHLY",
            "recurringCount": 120,
            "mobileNumber": "9883835373",
        }

        INDEX = "1"
        ENDPOINT = "/v3/recurring/subscription/create"
        SALTKEY = SaltKey
        base64String = base64_encode(payload)
        mainString = base64String + ENDPOINT + SALTKEY
        sha256Val = calculate_sha256_string(mainString)
        checkSum = sha256Val + '###' + INDEX

        headers = {
            'Content-Type': 'application/json',
            'X-Verify': checkSum,
        }

        json_data = {
            'request': base64String,
        }

        response = requests.post(
            f'{prodURL}/v3/recurring/subscription/create', headers=headers, json=json_data)

        response.raise_for_status()
        responseData = response.json()

        return responseData



    # Submit Auth API Request for UPI Collect
    def SubmitAuthRequestUPICollect(susubscriptionID, amount, authRequestId, upiID):
        sent_amount = amount * 100

        payload = {
            "merchantId": merchantID,
            "merchantUserId": 'FVSGHHSB3456AFFS89876GH',
            "subscriptionId": susubscriptionID,
            "authRequestId": authRequestId,
            "amount": sent_amount,
            "paymentInstrument": {
                "type": "UPI_COLLECT",
                "vpa": upiID
            }
        }

        INDEX = "1"
        ENDPOINT = "/v3/recurring/auth/init"
        SALTKEY = SaltKey
        base64String = base64_encode(payload)
        mainString = base64String + ENDPOINT + SALTKEY
        sha256Val = calculate_sha256_string(mainString)
        checkSum = sha256Val + '###' + INDEX

        headers = {
            'Content-Type': 'application/json',
            'X-Verify': checkSum,
            'X-CALLBACK-URL': f'{webhook_url}'
        }

        json_data = {
            'request': base64String,
        }

        response = requests.post(
            f'{prodURL}/v3/recurring/auth/init', headers=headers, json=json_data)

        response.raise_for_status()
        responseData = response.json()

        return responseData



    # Submit Auth API Request for UPI Collect
    def SubmitAuthRequestQR(susubscriptionID, amount, authRequestId):

        sent_amount = amount * 100

        payload = {
            "merchantId": merchantID,
            "merchantUserId": 'FVSGHHSB3456AFFS89876GH',
            "subscriptionId": susubscriptionID,
            "authRequestId": authRequestId,
            "amount": sent_amount,
            "paymentInstrument": {
                "type": "UPI_QR"
            }
        }

        INDEX = "1"
        ENDPOINT = "/v3/recurring/auth/init"
        SALTKEY = SaltKey
        base64String = base64_encode(payload)
        mainString = base64String + ENDPOINT + SALTKEY
        sha256Val = calculate_sha256_string(mainString)
        checkSum = sha256Val + '###' + INDEX

        headers = {
            'Content-Type': 'application/json',
            'X-Verify': checkSum,
            'X-CALLBACK-URL': f'{webhook_url}'
        }

        json_data = {
            'request': base64String,
        }

        response = requests.post(
            f'{prodURL}/v3/recurring/auth/init', headers=headers, json=json_data)

        response.raise_for_status()
        responseData = response.json()

        return responseData



    # Recurring Init API for monthly deduction
    def RecurringInit(susubscriptionID, amount, authRequestId):
        sent_amount = amount * 100
    
        payload = {
            "merchantId": merchantID,
            "merchantUserId": 'FVSGHHSB3456AFFS89876GH',
            "subscriptionId": susubscriptionID,
            "transactionId": authRequestId,
            "autoDebit": True,
            "amount": sent_amount
        }

        INDEX = "1"
        ENDPOINT = "/v3/recurring/debit/init"
        SALTKEY = SaltKey
        base64String = base64_encode(payload)
        mainString = base64String + ENDPOINT + SALTKEY
        sha256Val = calculate_sha256_string(mainString)
        checkSum = sha256Val + '###' + INDEX

        headers = {
            'Content-Type': 'application/json',
            'X-Verify': checkSum,
            'X-CALLBACK-URL': 'https://api.famousbusiness.in/premium-plan-api/recurring/payment/webhook/'
        }

        json_data = {
            'request': base64String,
        }


        response = requests.post(
            f'{prodURL}/v3/recurring/debit/init', headers=headers, json=json_data)

        response.raise_for_status()
        responseData = response.json()

        return responseData
    


    # Check submit auth status
    def CheckPaymentStatus(authRequestId):
        INDEX = "1"
        ENDPOINT = f"/v3/recurring/auth/status/{merchantID}/{authRequestId}"
        SALTKEY = SaltKey
        mainString = ENDPOINT + SALTKEY
        sha256Val = calculate_sha256_string(mainString)
        checkSum = sha256Val + '###' + INDEX

        headers = {
            'Content-Type': 'application/json',
            'X-VERIFY': checkSum,
        }

        response = requests.get(
            f'{prodURL}/v3/recurring/auth/status/{merchantID}/{authRequestId}', headers=headers)

        response.raise_for_status()
        responseData = response.json()

        return responseData
    

    def CancelSubscripton():
        pass




##### Penny Drop Payment
class PhoenepePennyDropAutopay:
    # Create User Subscription API
    def Create_user_Subscription(subscriptionID, amount):
        sent_amount = amount * 100

        payload = {
            "merchantId": merchantID,
            "merchantSubscriptionId": subscriptionID,
            "merchantUserId": "FVSGHHSB3456AFFS89876GH",
            "authWorkflowType": "PENNY_DROP",
            "amountType": "VARIABLE",
            "amount": sent_amount ,
            "frequency": "MONTHLY",
            "recurringCount": 120,
            "mobileNumber": "9883835373",
        }

        INDEX = "1"
        ENDPOINT = "/v3/recurring/subscription/create"
        SALTKEY = SaltKey
        base64String = base64_encode(payload)
        mainString = base64String + ENDPOINT + SALTKEY
        sha256Val = calculate_sha256_string(mainString)
        checkSum = sha256Val + '###' + INDEX

        headers = {
            'Content-Type': 'application/json',
            'X-Verify': checkSum,
        }

        json_data = {
            'request': base64String,
        }

        response = requests.post(
            f'{prodURL}/v3/recurring/subscription/create', headers=headers, json=json_data)

        response.raise_for_status()
        responseData = response.json()

        return responseData



    # Submit Auth API Request for UPI Collect
    def SubmitAuthRequestUPICollect(susubscriptionID, authRequestId, upiID):

        payload = {
            "merchantId": merchantID,
            "merchantUserId": 'FVSGHHSB3456AFFS89876GH',
            "subscriptionId": susubscriptionID,
            "authRequestId": authRequestId,
            "paymentInstrument": {
                "type": "UPI_COLLECT",
                "vpa": upiID
            }
        }

        INDEX = "1"
        ENDPOINT = "/v3/recurring/auth/init"
        SALTKEY = SaltKey
        base64String = base64_encode(payload)
        mainString = base64String + ENDPOINT + SALTKEY
        sha256Val = calculate_sha256_string(mainString)
        checkSum = sha256Val + '###' + INDEX

        headers = {
            'Content-Type': 'application/json',
            'X-Verify': checkSum,
            'X-CALLBACK-URL': f'{webhook_url}'
        }

        json_data = {
            'request': base64String,
        }

        response = requests.post(
            f'{prodURL}/v3/recurring/auth/init', headers=headers, json=json_data)

        response.raise_for_status()
        responseData = response.json()

        return responseData



    # Submit Auth API Request for UPI Collect
    def SubmitAuthRequestQR(susubscriptionID, authRequestId):

        payload = {
            "merchantId": merchantID,
            "merchantUserId": 'FVSGHHSB3456AFFS89876GH',
            "subscriptionId": susubscriptionID,
            "authRequestId": authRequestId,
            "paymentInstrument": {
                "type": "UPI_QR"
            }
        }

        INDEX = "1"
        ENDPOINT = "/v3/recurring/auth/init"
        SALTKEY = SaltKey
        base64String = base64_encode(payload)
        mainString = base64String + ENDPOINT + SALTKEY
        sha256Val = calculate_sha256_string(mainString)
        checkSum = sha256Val + '###' + INDEX

        headers = {
            'Content-Type': 'application/json',
            'X-Verify': checkSum,
            'X-CALLBACK-URL': f'{webhook_url}'
        }

        json_data = {
            'request': base64String,
        }

        response = requests.post(
            f'{prodURL}/v3/recurring/auth/init', headers=headers, json=json_data)

        response.raise_for_status()
        responseData = response.json()

        return responseData



