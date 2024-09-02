from django.urls import path
from .ads_view import ADPremiumPlanAPIView, ADSPaymentAPIView, AdsAPIView, ADPaymentCompleteAPIView



urlpatterns = [
     path('ad-plans/', ADPremiumPlanAPIView.as_view(), name='ad_premiumplan'),
     path('ad-payment/', ADSPaymentAPIView.as_view(), name='ad_payment'),
     path('ad-payment-complete/', ADPaymentCompleteAPIView.as_view(), name='ad_payment_complete'),
     path('post-ad/', AdsAPIView.as_view(), name='post_ad'),
]


