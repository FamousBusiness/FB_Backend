from django.urls import path
from .views import (
    BannerPremiumPlanAPIView, BannerPaymentAPIView, 
    BannerPaymentCompleteAPIView, BannerUploadAPIView
    )



urlpatterns = [
     path('banner-plans/', BannerPremiumPlanAPIView.as_view(), name='banner_premiumplan'),
     path('banner-payment/', BannerPaymentAPIView.as_view(), name='banner_payment'),
     path('banner-payment-complete/', BannerPaymentCompleteAPIView.as_view(), name='banner_payment_complete'),
     path('upload-banner-api/', BannerUploadAPIView.as_view(), name='upload_banner'),
]