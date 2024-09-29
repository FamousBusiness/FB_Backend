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





admin.site.register(PremiumPlan, PremiumplanModelAdmin)
admin.site.register(PlanDetail,  PlanDetainlModelAdmin)
admin.site.register(UserPremiumPlan)
admin.site.register(PlanCancelRequest)
admin.site.register(TrialPlanRequest)
admin.site.register(PremiumPlanBenefits)
admin.site.register(PremiumPlanOrder)
admin.site.register(PhonepeAutoPayOrder)

