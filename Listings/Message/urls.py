from django.urls import path
from .msg_views import MessagePaymentAPIView, MessagePaymentCompleteAPIView, MessagePremiumPlanAPIView, MessageSendAPIView



urlpatterns = [
    path('msg-payment/', MessagePaymentAPIView.as_view(), name='message_payment'),
    path('msg-payment-complete/', MessagePaymentCompleteAPIView.as_view(), name='message_payment_complete'),
    path('msg-plans/', MessagePremiumPlanAPIView.as_view(), name='msg_premiumplan'),
    path('msg-send/', MessageSendAPIView.as_view(), name='msg_send'),
    
]
