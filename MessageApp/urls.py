from django.urls import path
from .views import SendTESTSMSView, index, pay, payment_return, Payment_Successfull, LeadCheck, SendWhatsAppTestMessage


urlpatterns = [
    path('send-test-message/', SendTESTSMSView.as_view(), name='send_test_message'),
    path('send-test-whatsapp-message/', SendWhatsAppTestMessage.as_view(), name='send_test_whatsapp_message'),
    path('payment-home/', index, name='home_view'),
    path('pay/', pay, name='pay'),
    path('return-to-me/', payment_return, name='return_to_me'),
    path('payment-successfull/', Payment_Successfull, name='payment_successfull'),
    path('lead-check/', LeadCheck.as_view(), name='lead-check')
]




