from .import client
from rest_framework import status
from rest_framework.serializers import ValidationError




class RazorpayClient:
    def create_order(self, amount):
        data = {
            "amount": amount * 100,
            "currency": "INR",
        }

        try:
            self.order = client.order.create(data=data)
            return self.order
        
        except Exception as e:
            raise ValidationError(
                {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": e
                }
            )
    
    def verify_payment_signature(self, razorpay_order_id, razorpay_payment_id, razorpay_signature):

        try:
            self.verify_signature = client.utility.verify_payment_signature({
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature
            })
            return self.verify_signature
        
        except Exception as e:
            raise ValidationError(
                {
                    'staus_code': status.HTTP_400_BAD_REQUEST,
                    'message': e
                }
            )