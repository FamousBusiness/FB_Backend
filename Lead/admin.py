from django.contrib import admin
from Lead.models import (
    LeadPrice, LeadBucket, BusinessPageLead, BusinessPageLeadBucket, Lead, BusinessPageLeadView,
    ComboLead, ComboLeadBucket, AssignedLeadPerPremiumPlan, LeadOrder, ComboLeadOrder, LeadFormQuestion,
    LeadFrorm, LeadBanner, LeadFormTag, BannedLeadGroup, CategoryLeadViewQuantity
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


class LeadFormModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'headline', 'form_tag')


class LeadBannedGroupModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at',)
    search_fields = ('name',)


class CategoryLeadViewQuantityModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'quantity')
    search_fields = ('category',)
    ordering = ('-id',)



admin.site.register(CategoryLeadViewQuantity, CategoryLeadViewQuantityModelAdmin)
admin.site.register(BannedLeadGroup, LeadBannedGroupModelAdmin)
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
admin.site.register(LeadFormQuestion)
admin.site.register(LeadFrorm, LeadFormModelAdmin)
admin.site.register(LeadBanner)
admin.site.register(LeadFormTag)

