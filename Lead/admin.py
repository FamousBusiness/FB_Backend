from django.contrib import admin
from Lead.models import (
    LeadPrice, LeadBucket, BusinessPageLead, BusinessPageLeadBucket, Lead, BusinessPageLeadView,
    ComboLead, ComboLeadBucket, AssignedLeadPerPremiumPlan, LeadOrder, ComboLeadOrder
    )



class LeadPriceModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'price')

class BusinessPageLeadModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'business_page', 'created_at', 'status')


class LeadModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_by', 'category', 'mobile_number', 'email', 'created_at', 'expired', 'city', 'mail_sent')
    empty_value_display = "-empty-"

class BusinessPageLeadBucketModelAdmin(admin.ModelAdmin):
    list_display = ("id", "business_page", "lead", "is_paid")

class LeadBucketModelAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "lead", "is_paid", "viewed")



admin.site.register(Lead, LeadModelAdmin)
admin.site.register(LeadOrder)
admin.site.register(ComboLeadOrder)  
admin.site.register(BusinessPageLeadBucket, BusinessPageLeadBucketModelAdmin)
admin.site.register(LeadPrice, LeadPriceModelAdmin)
admin.site.register(LeadBucket, LeadBucketModelAdmin)
admin.site.register(BusinessPageLead, BusinessPageLeadModelAdmin)
admin.site.register(ComboLead)
admin.site.register(ComboLeadBucket)
admin.site.register(AssignedLeadPerPremiumPlan)
admin.site.register(BusinessPageLeadView)

