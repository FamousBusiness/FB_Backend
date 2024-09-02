from django.urls import path
from .mail_views import MailPremiumPlanAPIView, MailPaymentAPIView, MailPaymentCompleteAPIView, send_email, send_mail_template_testing



urlpatterns = [
    path('msg-payment/', MailPaymentAPIView.as_view(), name='message_payment'),
    path('msg-payment-complete/', MailPaymentCompleteAPIView.as_view(), name='message_payment_complete'),
    path('msg-plans/', MailPremiumPlanAPIView.as_view(), name='msg_premiumplan'),
    path('send-mail/', send_email, name='send_mail'),
    path('mail-template-testing/', send_mail_template_testing, name='send_mail'),
    # path('msg-send/', MailSendAPIView.as_view(), name='msg_send'),
]
