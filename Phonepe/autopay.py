from Phonepe.encoded import base64_encode, calculate_sha256_string
from decouple import config
import requests
from decouple import config



IS_DEVELOPMENT = config('IS_DEVELOPMENT')

if IS_DEVELOPMENT == 'True':
    webhook_url    = 'https://0f45-2409-4050-e38-e2f-d00e-68bf-c089-e6c0.ngrok-free.app/premium-plan-api/autopay/payment/webhook/'
    TestMerchantId = 'WEBZOTICAUAT'
    merchantID     = 'M22BWNC10OPNQ'
    TestsaltKey    = '9edb6a3f-bfd8-4e64-b325-355044c0e0bb' # test key
    SaltKey        = '083f0f7b-217c-4930-a6ba-49f6140376da'
else:
    webhook_url    = 'https://api.famousbusiness.in/premium-plan-api/autopay/payment/webhook/'
    TestMerchantId = 'WEBZOTICAUAT'
    merchantID     = 'M22BWNC10OPNQ'
    TestsaltKey    = '9edb6a3f-bfd8-4e64-b325-355044c0e0bb' # test key
    SaltKey        = '083f0f7b-217c-4930-a6ba-49f6140376da'



# Phonepe Autopay
class PremiumPlanPhonepeAutoPayPayment:
        
    # Create User Subscription API
    def Create_user_Subscription(subscriptionID, userID, amount):

        sent_amount = amount * 100

        payload = {
            "merchantId": TestMerchantId,
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
        SALTKEY = TestsaltKey
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
            'https://api-preprod.phonepe.com/apis/pg-sandbox/v3/recurring/subscription/create', headers=headers, json=json_data)

        response.raise_for_status()
        responseData = response.json()

        return responseData



    # Submit Auth API Request for UPI Collect
    def SubmitAuthRequestUPICollect(susubscriptionID, userID, amount, authRequestId, upiID):

        sent_amount = amount * 100

        payload = {
            "merchantId": TestMerchantId,
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
        SALTKEY = TestsaltKey
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
            'https://api-preprod.phonepe.com/apis/pg-sandbox/v3/recurring/auth/init', headers=headers, json=json_data)

        response.raise_for_status()
        responseData = response.json()

        return responseData



    # Submit Auth API Request for UPI Collect
    def SubmitAuthRequestQR(susubscriptionID, userID, amount, authRequestId):

        sent_amount = amount * 100

        payload = {
            "merchantId": TestMerchantId,
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
        SALTKEY = TestsaltKey
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
            'https://api-preprod.phonepe.com/apis/pg-sandbox/v3/recurring/auth/init', headers=headers, json=json_data)

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
            'https://api-preprod.phonepe.com/apis/pg-sandbox/v3/recurring/debit/init', headers=headers, json=json_data)

        response.raise_for_status()
        responseData = response.json()

        print(responseData)
        return responseData
    

    # Check subnit auth status
    def CheckPaymentStatus(authRequestId):
        INDEX = "1"
        ENDPOINT = f"/v3/recurring/auth/status/{TestMerchantId}/{authRequestId}"
        SALTKEY = TestsaltKey
        mainString = ENDPOINT + SALTKEY
        sha256Val = calculate_sha256_string(mainString)
        checkSum = sha256Val + '###' + INDEX

        headers = {
            'Content-Type': 'application/json',
            'X-VERIFY': checkSum,
        }

        response = requests.get(
            f'https://api-preprod.phonepe.com/apis/pg-sandbox/v3/recurring/auth/status/{TestMerchantId}/{authRequestId}', headers=headers)

        response.raise_for_status()
        responseData = response.json()

        return responseData
    

    def CancelSubscripton():
        pass



