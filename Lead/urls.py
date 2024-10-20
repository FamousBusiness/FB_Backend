from django.urls import path
from .views import (
    EnquiryFormAPIView, BusinessPageLeadAPIView, AllLeadWithoutAllDataView, 
    ShowBusinessPageAssignedLeadView, LeadPaymentAPIView, LeadExcelUploadView, LeadCheckView,
    ComboLeadPaymentInitiationView, ComboLeadPaymentCompleteView, IDWiseComboLeadView, ComboLeadCheckAfterPaymentCompleteView,
    LeadPaymentCompleteView, ViewLeadData
    # welcome, pay, payment_return
    )



urlpatterns = [
    path('enquiry-form/', EnquiryFormAPIView.as_view(), name='enquiry_form_api'),
    path('individual-business-page-leads/', BusinessPageLeadAPIView.as_view(), name='individual_leads'),
    path('all-leads/<str:city>/<str:state>/', AllLeadWithoutAllDataView.as_view(), name='get_all_leads'),
    #View Lead Data
    path('business-page-lead-view/', ViewLeadData.as_view(), name='show-business-lead-data'),
    # path('business-page-lead-view/', ShowBusinessPageAssignedLeadView.as_view(), name='show-business-lead-data'),
    path('lead-payment/', LeadPaymentAPIView.as_view(), name='lead-payment'),
    path('lead-payment-complete/', LeadPaymentCompleteView, name='lead-payment-complete'),

    #Lead Excel Upload
    path('lead-excel-upload/', LeadExcelUploadView.as_view(), name='lead_excel_upload'),

    #Combo Lead
    path('combo-lead-payment/', ComboLeadPaymentInitiationView.as_view(), name='combo_lead_payment_initiation'),
    path('combo-lead-payment-complete/', ComboLeadPaymentCompleteView.as_view(), name='combo_lead_payment_complete'),
    
    path('individual-combo-lead/<combo_id>/', IDWiseComboLeadView.as_view(), name='id_wise_combo_lead'),
    path('combo-lead-check/', ComboLeadCheckAfterPaymentCompleteView.as_view(), name='combo_lead_check'),
    path('lead-check/', LeadCheckView.as_view(), name='lead_check'),
    # path('category-lead/', CategoryLeadApiView.as_view(), name='lead_generation_by_category'),
    
    path('fb-lead-capture/', LeadCheckView.as_view(), name='fb_auto_lead_capture'),
    # path('initiation/', welcome, name='welcome'),
    # path('pay/', pay, name='pay'),
    # path('return-to-me/', payment_return, name='payment_return'),
]



