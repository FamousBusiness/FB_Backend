from django.urls import path
from .admin_views import (
    AdminPanelAPIView,AdminADApproveAPIView, AdminJobApproveAPIView,
    AdminMessageApproveAPIView, ListingsExcelUploadAPIView, AdminBannerApproveAPIView
    )

urlpatterns = [
    path('', AdminPanelAPIView.as_view(), name='admin_panel'),
    path('ad-approval/', AdminADApproveAPIView.as_view(), name='admin_ad_approval'),
    path('ad-approval/<int:id>/', AdminADApproveAPIView.as_view(), name='admin_ad_approval'),
    path('msg-approval/', AdminMessageApproveAPIView.as_view(), name='admin_msg_approval'),
    path('msg-approval/<int:id>/', AdminMessageApproveAPIView.as_view(), name='admin_msg_approval'),
    path('banner-approve-api/', AdminBannerApproveAPIView.as_view(), name='admin_banner_approval'),
    path('banner-approve-api/<int:id>/', AdminBannerApproveAPIView.as_view(), name='admin_banner_approval'),
    path('job-approve-api/', AdminJobApproveAPIView.as_view(), name='admin_job_approval'),
    path('job-approve-api/<int:id>/', AdminJobApproveAPIView.as_view(), name='admin_job_approval'),
    path('excel-upload/', ListingsExcelUploadAPIView.as_view(), name='excel_upload'),
]
