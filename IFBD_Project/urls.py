from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken import views
from rest_framework_simplejwt.views import TokenBlacklistView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView, TokenVerifyView
)




urlpatterns = [
    path('admin/', admin.site.urls, name='admin_panel'),

    path('api/', include('users.urls')),

    path('api/listings/', include('Listings.urls')),
    path('razorpay/', include('Listings.RazorpayPayment.urls')),
    
    path('msg/', include('Listings.Message.urls')),
    path('mail/', include('Listings.Mail.urls')),
    path('transaction-api/', include('Listings.Transaction.urls')),

    path('banner/', include('Banner.urls')),
    
    path('brand-api/', include('Brands.urls')),
    
    path('premium-plan-api/', include('PremiumPlan.urls')),

    path('lead-api/', include('Lead.urls')),

    path('job-api/', include('JOB.urls')),

    path('soft-api/', include('Software.urls')),

    path('ads-api/', include('ADS.urls')),

    path('messenger-api/', include('Messenger.urls')),

    path('mail-api/', include('MailApp.urls')),

    path('message-api/', include('MessageApp.urls')),

    # path('admin-auth/', include('Admin.urls')),

    path('', include('Admin.urls')),

    path('api-token-auth/', views.obtain_auth_token),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='verify-token'),
    # path("__debug__/", include("debug_toolbar.urls")),   
]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

