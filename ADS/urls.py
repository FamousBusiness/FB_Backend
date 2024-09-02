from django.urls import path
from ADS import views


urlpatterns = [
    path('ad-plans/', views.AllADPlansAPIView.as_view(), name='all_ad_plans'),
    path('ad-payment/', views.ADPaymentInitiateAPIView.as_view(), name='ad_payment_initiation'),
    path('ad-payment-complete/', views.ADPaymentCompleteAPIView.as_view(), name='ad_payment_complete'),
]


