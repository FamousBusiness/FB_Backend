from Phonepe.encoded import base64_encode, calculate_sha256_string
from decouple import config
import requests
from decouple import config



IS_DEVELOPMENT = config('IS_DEVELOPMENT')

if IS_DEVELOPMENT == 'True':
    webhook_url    = 'https://8aee-2405-204-1389-91d5-1de0-c93-c74f-968d.ngrok-free.app/premium-plan-api/autopay/payment/webhook/'
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
            "merchantUserId": userID,
            "authWorkflowType": "TRANSACTION",
            "amountType": "FIXED",
            "amount": sent_amount ,
            "frequency": "DAILY",
            "recurringCount": 3,
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
    def SubmitAuthRequestUPICollect(susubscriptionID, userID, amount, authRequestId, upiID):

        sent_amount = amount * 100

        payload = {
            "merchantId": merchantID,
            "merchantUserId": userID,
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
    def SubmitAuthRequestQR(susubscriptionID, userID, amount, authRequestId):

        sent_amount = amount * 100

        payload = {
            "merchantId": merchantID,
            "merchantUserId": userID,
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
    def RecurringInit(susubscriptionID, userID, amount, authRequestId):

        sent_amount = amount * 100
        
        payload = {
            "merchantId": TestMerchantId,
            "merchantUserId": userID,
            "subscriptionId": susubscriptionID,
            "transactionId": authRequestId,
            "autoDebit": True,
            "amount": sent_amount
        }

        INDEX = "1"
        ENDPOINT = "/v3/recurring/debit/init"
        SALTKEY = TestsaltKey
        base64String = base64_encode(payload)
        mainString = base64String + ENDPOINT + SALTKEY
        sha256Val = calculate_sha256_string(mainString)
        checkSum = sha256Val + '###' + INDEX

        headers = {
            'Content-Type': 'application/json',
            'X-Verify': checkSum,
            'X-CALLBACK-URL': 'https://webhook.site/14c7dd78-d157-4222-b34c-1b5aff841d37'
        }

        json_data = {
            'request': base64String,
        }


        response = requests.post(
            f'{prodURL}/v3/recurring/debit/init', headers=headers, json=json_data)

        response.raise_for_status()
        responseData = response.json()


        return responseData
    

    # Check subnit auth status
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



