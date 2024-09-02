from django.contrib import admin
from ADS.models import ADS, ADPLANS, Orders, ADImage, UserADView, AdBucket



class ADSModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'is_active', 'city', 'verified')
    




admin.site.register(ADS, ADSModelAdmin)
admin.site.register(ADPLANS)
admin.site.register(Orders)
admin.site.register(ADImage)
admin.site.register(UserADView)
admin.site.register(AdBucket)



