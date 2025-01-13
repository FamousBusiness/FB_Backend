from django.urls import path
from users import views
# from django.contrib.auth.views import LoginView



urlpatterns = [
    path('', views.home_view, name='home_page'),
    path('register/', views.UserRegisterAPIView.as_view(), name='register'),
    path('client-register/', views.ClientRegisterAPIView.as_view(), name='client_register'),
    path('login/', views.LoginAuthAPIView.as_view(), name='login'),
    path('logout/', views.LogoutAPIView.as_view(), name='logout'),
    path('changepassword/', views.UserChangePasswordView.as_view(), name='change-password'),
    path('send-reset-password-mail/', views.UserPasswordResetMailView.as_view(), name='send-rest-password-mail'),
    path('reset-password/<uid>/<token>/', views.UserPasswordResetView.as_view(), name='reset-password'),
    path('user-business-page/<int:business_id>/', views.UserBusinessPageAPIView.as_view(), name='user-business-page'),
    path('user-business-page/', views.UserBusinessPageAPIView.as_view(), name='user-business-page'),
    path('mail-register/<uid>/<token>/', views.MailRegisterView.as_view(), name='mail_register'),
    path('ip-address/', views.ip_view, name='mail_register'),

    path('send/login/otp/', views.SendLoginOTPView.as_view(), name='send_login_otp'),
    path('login/otp/', views.LoginUserThroughOTP.as_view(), name='send_login_otp'),
    
    #CSRF Token
    # path('csrf-token/', views.GetCSRFTokenView.as_view(), name='get_csrf_token'),
    path('isauthenticated/', views.CheckAuthenticatedView.as_view(), name='is_authenticated'),
    path('fetch/users/', views.GetUsersAccordingtoMobileNumber.as_view(), name='fetch_users'),
    # path('loggedin-user/', views.render_logged_in_user_list, name='user-business-page'),
    # path('otp/<str:uid>/', views.ValidateOTP.as_view(), name='otp'),
    # path('otp/<str:uid>/', views.otpVerify, name='otp'),
]


