from django.urls import path
from Software import views



urlpatterns = [
    path('payment-initiate/', views.SoftwarePaymentInitiationAPIView.as_view(), name='Initiate_Payment'),
    path('payment-complete/', views.SoftwarePaymentCompletView.as_view(), name='complete_Payment')
]
