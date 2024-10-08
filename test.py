import requests
import json
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend




def base64_encode(input_dict):
    json_data = json.dumps(input_dict)
    data_bytes = json_data.encode('utf-8')
    return base64.b64encode(data_bytes).decode('utf-8')


def calculate_sha256_string(input_string):
    sha256 = hashes.Hash(hashes.SHA256(), backend=default_backend())
    sha256.update(input_string.encode('utf-8'))
    return sha256.finalize().hex()



TestMerchantID = 'WEBZOTICAUAT'
TestSaltKey    = '9edb6a3f-bfd8-4e64-b325-355044c0e0bb'

ProdMerchantID = 'M22BWNC10OPNQ'
ProdSaltKey    = '083f0f7b-217c-4930-a6ba-49f6140376da'



# Phonepe Autopay
# class PremiumPlanPhonepeAutoPayPayment:
        
#     # Create User Subscription API
#     def Create_user_Subscription(subscriptionID, userID, amount):

#         sent_amount = amount * 100

#         payload = {
#             "merchantId": ProdMerchantID,
#             "merchantSubscriptionId": subscriptionID,
#             "merchantUserId": userID,
#             "authWorkflowType": "TRANSACTION",
#             "amountType": "FIXED",
#             "amount": sent_amount ,
#             "frequency": "DAILY",
#             "recurringCount": 3,
#             "mobileNumber": "9883835373",
#         }

#         INDEX = "1"
#         ENDPOINT = "/v3/recurring/subscription/create"
#         SALTKEY = ProdSaltKey
#         base64String = base64_encode(payload)
#         mainString = base64String + ENDPOINT + SALTKEY
#         sha256Val = calculate_sha256_string(mainString)
#         checkSum = sha256Val + '###' + INDEX

#         headers = {
#             'Content-Type': 'application/json',
#             'X-Verify': checkSum,
#         }

#         json_data = {
#             'request': base64String,
#         }

#         response = requests.post(
#             f'https://mercury-t2.phonepe.com/v3/recurring/subscription/create', headers=headers, json=json_data)

#         response.raise_for_status()
#         responseData = response.json()

#         return responseData



#     # Submit Auth API Request for UPI Collect
#     def SubmitAuthRequestUPICollect(susubscriptionID, userID, amount, authRequestId, upiID):
#         sent_amount = amount * 100

#         payload = {
#             "merchantId": ProdMerchantID,
#             "merchantUserId": userID,
#             "subscriptionId": susubscriptionID,
#             "authRequestId": authRequestId,
#             "amount": sent_amount,
#             "paymentInstrument": {
#                 "type": "UPI_COLLECT",
#                 "vpa": upiID
#             }
#         }

#         INDEX = "1"
#         ENDPOINT = "/v3/recurring/auth/init"
#         SALTKEY = ProdSaltKey
#         base64String = base64_encode(payload)
#         mainString = base64String + ENDPOINT + SALTKEY
#         sha256Val = calculate_sha256_string(mainString)
#         checkSum = sha256Val + '###' + INDEX

#         headers = {
#             'Content-Type': 'application/json',
#             'X-Verify': checkSum,
#             'X-CALLBACK-URL': 'https://webhook.site/8ed604ea-483e-4a2c-96ff-c60cd2099ab6'
#         }

#         json_data = {
#             'request': base64String,
#         }

#         response = requests.post(
#             f'https://mercury-t2.phonepe.com/v3/recurring/auth/init', headers=headers, json=json_data)

#         response.raise_for_status()
#         responseData = response.json()

#         return responseData



#     # Submit Auth API Request for UPI Collect
#     def SubmitAuthRequestQR(susubscriptionID, userID, amount, authRequestId):
#         sent_amount = amount * 100

#         payload = {
#             "merchantId": ProdMerchantID,
#             "merchantUserId": userID,
#             "subscriptionId": susubscriptionID,
#             "authRequestId": authRequestId,
#             "amount": sent_amount,
#             "paymentInstrument": {
#                 "type": "UPI_QR"
#             }
#         }

#         INDEX = "1"
#         ENDPOINT = "/v3/recurring/auth/init"
#         SALTKEY = ProdSaltKey
#         base64String = base64_encode(payload)
#         mainString = base64String + ENDPOINT + SALTKEY
#         sha256Val = calculate_sha256_string(mainString)
#         checkSum = sha256Val + '###' + INDEX

#         headers = {
#             'Content-Type': 'application/json',
#             'X-Verify': checkSum,
#             'X-CALLBACK-URL': 'https://webhook.site/8ed604ea-483e-4a2c-96ff-c60cd2099ab6'
#         }

#         json_data = {
#             'request': base64String,
#         }

#         response = requests.post(
#             f'https://mercury-t2.phonepe.com/v3/recurring/auth/init', headers=headers, json=json_data)

#         response.raise_for_status()
#         responseData = response.json()

#         return responseData
    




### Start
def Create_user_Subscription():

        payload = {
            "merchantId": ProdMerchantID,
            "merchantSubscriptionId": 'shdhggh-6777hsh-shdn8788',
            "merchantUserId": "FGHJJHFGGT566",
            "authWorkflowType": "TRANSACTION",
            "amountType": "FIXED",
            "amount": 100 ,
            "frequency": "DAILY",
            "recurringCount": 5,
            "mobileNumber": "9883835373",
        }

        INDEX = "1"
        ENDPOINT = "/v3/recurring/subscription/create"
        SALTKEY = ProdSaltKey
        base64String = base64_encode(payload)
        mainString = base64String + ENDPOINT + SALTKEY
        sha256Val = calculate_sha256_string(mainString)
        checkSum = sha256Val + '###' + INDEX

        print('base64String', base64String)

        print('checkSum', checkSum)


        # headers = {
        #     'Content-Type': 'application/json',
        #     'X-Verify': checkSum,
        # }

        # json_data = {
        #     'request': base64String,
        # }

        # response = requests.post(
        #     f'https://mercury-t2.phonepe.com/v3/recurring/subscription/create', headers=headers, json=json_data)

        # response.raise_for_status()
        # responseData = response.json()

        # return responseData


# Create_user_Subscription()


# Submit Auth API Request for UPI Collect
def SubmitAuthRequestUPICollect():

    payload = {
        "merchantId": ProdMerchantID,
        "merchantUserId": "FGHJJHFGGT566",
        "subscriptionId": "OMS2410072314453333705926D",
        "authRequestId": "Bhgsdhgdg-0987hshd-isns-67H87567",
        "amount": 100,
        "paymentInstrument": {
            "type": "UPI_COLLECT",
            "vpa": "sahooranjitkumar53@ybl"
        }
    }


    INDEX = "1"
    ENDPOINT = "/v3/recurring/auth/init"
    SALTKEY = ProdSaltKey
    base64String = base64_encode(payload)
    mainString = base64String + ENDPOINT + SALTKEY
    sha256Val = calculate_sha256_string(mainString)
    checkSum = sha256Val + '###' + INDEX

    print('base64String', base64String)

    print('checkSum', checkSum)

    # headers = {
    #     'Content-Type': 'application/json',
    #     'X-Verify': checkSum,
    #     'X-CALLBACK-URL': 'https://webhook.site/8ed604ea-483e-4a2c-96ff-c60cd2099ab6'
    # }

    # json_data = {
    #     'request': base64String,
    # }

    # response = requests.post(
    #     f'https://mercury-t2.phonepe.com/v3/recurring/auth/init', headers=headers, json=json_data)

    # response.raise_for_status()
    # responseData = response.json()

    # return responseData


# SubmitAuthRequestUPICollect()


# Submit Auth API Request for UPI Collect
def SubmitAuthRequestQR():

    payload = {
        "merchantId": ProdMerchantID,
        "merchantUserId": 'FGHJJHFGGT566',
        "subscriptionId": 'OMS2410072314453333705926D',
        "authRequestId": 'hsggdg-677hhvs-duhds788',
        "amount": 100,
        "paymentInstrument": {
            "type": "UPI_QR"
        }
    }

    INDEX = "1"
    ENDPOINT = "/v3/recurring/auth/init"
    SALTKEY = ProdSaltKey
    base64String = base64_encode(payload)
    mainString = base64String + ENDPOINT + SALTKEY
    sha256Val = calculate_sha256_string(mainString)
    checkSum = sha256Val + '###' + INDEX

    print('base64String', base64String)

    print('checkSum', checkSum)
    # headers = {
    #     'Content-Type': 'application/json',
    #     'X-Verify': checkSum,
    #     'X-CALLBACK-URL': 'https://webhook.site/8ed604ea-483e-4a2c-96ff-c60cd2099ab6'
    # }

    # json_data = {
    #     'request': base64String,
    # }

    # response = requests.post(
    #     f'https://mercury-t2.phonepe.com/v3/recurring/auth/init', headers=headers, json=json_data)

    # response.raise_for_status()
    # responseData = response.json()

    # return responseData


# SubmitAuthRequestQR()
