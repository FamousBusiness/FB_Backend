from django.db import models
from users.models import User
from Listings.models import Category
from django.utils import timezone
from datetime import timedelta
from django.utils.translation import gettext_lazy as _
from Listings.constants import PaymentStatus
import random
import string




ADS_CONDITION = [
    ('Almost Like New', 'Almost Like New'),
    ('Brand New', 'Brand New'),
    ('Gently used', 'Gentky used'),
    ('Heavily used', 'Heavily used'),
    ('Unboxed', 'Unboxed'),
]

AD_STATUS = [
    ('Pending', 'Pending'),
    ('Approved', 'Approved'),
    ('Active', 'Active'),
    ('Rejected', 'Rejected'),
]




class ADS(models.Model):
    ad_id         = models.CharField(max_length=50, unique=True, editable=False)
    posted_by     = models.ForeignKey(User, on_delete=models.CASCADE)
    title         = models.CharField(max_length=80)
    category      = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    city          = models.CharField(max_length=50)
    condition     = models.CharField(choices=ADS_CONDITION,max_length=16)
    is_active     = models.BooleanField(default=False)
    verified      = models.BooleanField(default=False)
    views         = models.BigIntegerField(default=0)
    status        = models.CharField(max_length=10, choices=AD_STATUS, default='Pending')


    def save(self, *args, **kwargs):
        self.ad_id = self.generarate_unique_id()
        super().save(*args, **kwargs)

    def generarate_unique_id(self):
        text_part = ''.join(random.choices(string.ascii_letters, k=8))
        numeric_part = str(random.randint(1000, 99999))

        return f"{text_part}{numeric_part}"

   
    def __str__(self):
        return f'Ads posted by {self.posted_by.name}'
    
    class Meta:
        ordering = ["-id"]



class ADImage(models.Model):
    ad    = models.ForeignKey(ADS, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(default='AD_Images/default.jpg', upload_to='AD_Images/')


    def __str__(self):
        return f"{self.pk}"



class ADPLANS(models.Model):
    name           = models.CharField(_("Plan Name"))
    views_quantity = models.BigIntegerField(_("Views Quantity"),default=0)
    price          = models.CharField(_("Price"), default="0")


    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        ordering = ["-id"]
    



class Orders(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    ad         = models.ForeignKey(ADS, on_delete=models.SET_NULL, null=True, blank=True)
    ad_plan    = models.ForeignKey(ADPLANS, on_delete=models.SET_NULL, null=True, blank=True)
    amount     = models.FloatField(_("Amount"), null=False, blank=False)
    order_date = models.DateTimeField(auto_now=True)
    isPaid     = models.BooleanField(default=False)
    details    = models.CharField(max_length=225, blank=True, null=True, verbose_name='Payment Details')
    status     = models.CharField(_("Payment Status"),default=PaymentStatus.PENDING, max_length=50,
        blank=False,
        null=False,
    )
    provider_order_id = models.CharField(
        _("Order ID"), max_length=40, null=False, blank=False
    ) 
    payment_id = models.CharField(
        _("Payment ID"), max_length=36, null=False, blank=False
    )
    signature_id = models.CharField(
        _("Signature ID"), max_length=128, null=False, blank=False
    )


    def __str__(self):
        return f"{self.pk}-{self.status}"
    

    class Meta:
        ordering = ["-id"]
    


    
class AdBucket(models.Model):
    posted_by     = models.ForeignKey(User, on_delete=models.CASCADE)
    ad_plan       = models.ForeignKey(ADPLANS, on_delete=models.SET_NULL, null=True)
    ad            = models.ForeignKey(ADS, on_delete=models.CASCADE)
    assigned_view = models.BigIntegerField(default=0)
    viewed        = models.BigIntegerField(default=0)
    is_paid       = models.BooleanField(default=False)
    is_active     = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.posted_by.name}\'s {self.ad_plan.name}"
    
    def save(self, *args, **kwargs):
       if self.assigned_view == 0:
           self.is_active = False
       
       super(AdBucket, self).save(*args, **kwargs)



class UserADView(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    ad         = models.ForeignKey(ADS, on_delete=models.CASCADE)
    is_viewed  = models.BooleanField(default=False)
    is_clicked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.ad.title} viewed by {self.user.name}"
    

    

