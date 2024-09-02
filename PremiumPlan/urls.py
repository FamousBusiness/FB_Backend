from django.urls import path
from .views import (
    AllPremiumPlanView, PremiumPlanPaymentView, PremiumPlanPaymentCompleteView, CancelPlanView,
    PremiumPlanPerUserView, TrialPlanActivationView, TrialPlanAdminApprovalView
    )





urlpatterns = [
    path('', AllPremiumPlanView.as_view(), name='All Premium Plan'),
    path('premium-plan-payment/', PremiumPlanPaymentView.as_view(), name='Premium Plan Payment'),
    path('premium-plan-payment-complete/', PremiumPlanPaymentCompleteView.as_view(), name='Premium Plan Payment Complete'),
    path('cancel-plan/<int:plan>/', CancelPlanView.as_view(), name='Cancel_Premium_Plan'),
    path('plan-per-user/', PremiumPlanPerUserView.as_view(), name='premium-plan-dashboard'),
    path('trial-plan-activation/', TrialPlanActivationView.as_view(), name='trial_plan_activation'),
    path('trial-plan-approval/', TrialPlanAdminApprovalView.as_view(), name='trial_plan_approval'),
]

