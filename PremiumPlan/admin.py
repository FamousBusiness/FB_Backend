from django.contrib import admin
from .models import (PremiumPlan, PlanDetail, UserPremiumPlan, 
                     PlanCancelRequest, TrialPlanRequest, PremiumPlanBenefits, 
                     PremiumPlanOrder, PhonepeAutoPayOrder
                     )




class PremiumplanModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'plan', 'lead_view', 'job_post')
    ordering = ('id',)
    empty_value_display = "-empty-"


class PlanDetainlModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'duration')
    ordering = ('id', 'name')
    empty_value_display = "-empty-"


@admin.register(PremiumPlanOrder)
class PremiumPlanOrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_id', 'amount', 'status', 'purchased_at', 'isPaid', 'repayment_date', 'invoice_no')
    search_fields = ('user__username', 'transaction_id', 'status', 'invoice_no')
    list_filter = ('status', 'isPaid', 'purchased_at')
    ordering = ('-purchased_at',)


@admin.register(PremiumPlanBenefits)
class PremiumPlanBenefitsAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'lead_assigned', 'is_paid', 'expired', 'purchased_at')
    search_fields = ('user__username', 'plan__name')
    list_filter = ('is_paid', 'expired', 'purchased_at')
    ordering = ('-purchased_at',)



@admin.register(PhonepeAutoPayOrder)
class PhonepeAutoPayOrderModelAdmin(admin.ModelAdmin):
    list_display  = ('premium_plan_id', 'user_id', 'MerchantSubscriptionId', 'amount')
    search_fields = ('premium_plan_id', 'user_id', 'MerchantSubscriptionId', 'amount')
    list_filter   = ('premium_plan_id', 'user_id', 'amount')
    ordering      = ('-id',)



admin.site.register(PremiumPlan, PremiumplanModelAdmin)
admin.site.register(PlanDetail,  PlanDetainlModelAdmin)
admin.site.register(UserPremiumPlan)
admin.site.register(PlanCancelRequest)
admin.site.register(TrialPlanRequest)

