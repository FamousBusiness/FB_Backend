from django.urls import path
from .import views



urlpatterns = [
    path('', views.AdminDashBoardView, name='home_page'),
    path('excel-upload/', views.AdminExcelUploadView, name='users_excel_upload'),
    path('password-reset/<uid>/', views.PasswordResetAfterMailView.as_view(), name='password_reset_before_page_owner'),
    path('aws-email-list/', views.AWSBounceMailListView.as_view(), name='aws_email_list'),

    #Premium Plans
    path('purchased-plan/', views.PurchasedPremiumPlanView.as_view(), name='purchased_plans'),
    path('plan-orders/', views.PremumPlanOrderView.as_view(), name='plan_orders'),
    path('active-plans/', views.AllActivePremiumPlanView.as_view(), name='all_active_plans'),
    path('deduct/periodic/payment/', views.DuductPeriodicPaymentView.as_view(), name='deduct_periodic_payment'),

    #Lead
    path('users-lead/', views.UsersPurchasedLeadView.as_view(), name='users_purchased_lead'),
    path('business-purchased-lead/', views.BusinessOwnerPurchasedLeadView.as_view(), name='business_purchased_lead'),
    path('all-leads/', views.AllLeadView.as_view(), name='all_availble_leads'),

    #User and Business Details
    path('all-users/', views.AllUsersDetailView.as_view(), name='all_users_data'),
    path('user-update/<int:pk>/', views.UserUpdateView.as_view(), name='admin_user_update'),
    path('all-business/', views.AllBusinessPageDetailView.as_view(), name='all_business_data'),
    path('business-update/<int:pk>/', views.BusinessUpdateView.as_view(), name='admin_business_update'),
    
    path('login-redirect/', views.LoginRedirectView, name='login_redirect'),
    path('google-login/', views.GoogleLoginView, name='google_login'),
]


