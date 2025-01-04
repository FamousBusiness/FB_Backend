from django.urls import path
from MailApp import views



urlpatterns = [
   path('send-test-mail/', views.SendTestMail, name='send_test_mail'), 
   path('send-manual-mail/', views.ManuallMailView, name='send_manual_mail'), 
   path('send-business-mail/', views.SendMailToBusinessOwnerWiseView, name='send_category_wise_business_mail'),
   path('generate/pdf/', views.generate_pdf_from_html, name='generate_pdf'),
]

