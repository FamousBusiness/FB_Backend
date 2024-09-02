from django.urls import path
from .razorpay_view import RazorpayOrderAPIView, CompletePaymentAPIView


urlpatterns = [
     path("order/create/", 
        RazorpayOrderAPIView.as_view(), 
        name="razorpay-create-order-api"
    ),
    path("order/complete/", 
        CompletePaymentAPIView.as_view(), 
        name="razorpay-complete-order-api"
    ),
]
