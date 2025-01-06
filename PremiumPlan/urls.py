from django.urls import path
from .views import (
    AllPremiumPlanView, PremiumPlanPaymentView, PremiumPlanPaymentCompleteView, CancelPlanView,
    PremiumPlanPerUserView, TrialPlanActivationView, TrialPlanAdminApprovalView, PaythorughUPIID,
    ReceivePhonepeAutoPayWebhook, AutoPayPaymentStatusCheck, RecurringInitPaymentView, RecurringPaymentWebhook
    )





urlpatterns = [
    path('', AllPremiumPlanView.as_view(), name='All Premium Plan'),
    path('premium-plan-payment/', PremiumPlanPaymentView.as_view(), name='Premium Plan Payment'), # Premium plan payment 1st
    path('autopay/upi/payment/', PaythorughUPIID.as_view(), name='Pay through UPI'), # Premium plan payment 2nd
    path('autopay/payment/webhook/', ReceivePhonepeAutoPayWebhook.as_view(), name='Autopay Webhook'), # Autopay Webhook
    path('autopay/payment/status/', AutoPayPaymentStatusCheck.as_view(), name='Autopay Payment Status'), # Autopay Payment Status
    path('recurring/payment/', RecurringInitPaymentView.as_view(), name='Recurring Payment API'), # Autopay Payment Status
    path('recurring/payment/webhook/', RecurringPaymentWebhook.as_view(), name='Recurring Payment Webhook'), # Monthly payment deduction Webhook

    path('premium-plan-payment-complete/', PremiumPlanPaymentCompleteView.as_view(), name='Premium Plan Payment Complete'), # Webhook
    path('cancel-plan/<int:plan>/', CancelPlanView.as_view(), name='Cancel_Premium_Plan'),
    path('plan-per-user/', PremiumPlanPerUserView.as_view(), name='premium-plan-dashboard'),
    path('trial-plan-activation/', TrialPlanActivationView.as_view(), name='trial_plan_activation'),
    path('trial-plan-approval/', TrialPlanAdminApprovalView.as_view(), name='trial_plan_approval')
]


