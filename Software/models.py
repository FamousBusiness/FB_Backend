from django.db import models
from users.models import User
from django.utils.translation import gettext_lazy as _


# SOFTWARE_CHOICE = (
#     ("Mobile App"), ("Mobile App"),
#     ("Web App"), ("Web App"),
# )

# class SoftwareProducts(models.Model):
#     name  = models.CharField(_("Product Name"),max_length = 100)
#     url   = models.URLField(_("Demo URL"),null=True, blank=True)
#     price = models.CharField(_("Price"),max_length=10)
#     image = models.ImageField(_("Product Picture"),null=True, blank=True)
#     type  = models.CharField(choices=SOFTWARE_CHOICE, max_length=15)


#     def __str__(self):
#         return f"{self.name} {self.type}"


class SoftwareOrder(models.Model):
    user               = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id     = models.CharField(_("Transaction ID"), max_length=100, unique=True)
    amount             = models.PositiveIntegerField(_("Amount"), null=True, blank=False)
    provider_reference_id  = models.CharField(
        _("Provider Reference ID"), max_length=80, null=False, blank=False
    )
    merchant_id        = models.CharField(_("Merchant ID"), null=False, blank=False)
    merchant_order_id  = models.CharField(_("Merchant Order ID"), null=True, blank=True, max_length=100)
    checksum           = models.CharField(_("Checksum"), null=True, blank=True)
    status             = models.CharField(_("Payment Status"), default="Pending", max_length=254,
        blank=False,
        null=False,
    )
    details            = models.CharField(max_length=255, null=True, blank=True)
    currency           = models.CharField(max_length=50, default='INR')
    message            = models.CharField(_("Phonepe Message"), default="Phonpe Message", blank=True, null=True, max_length=100)
    purchased_at       = models.DateTimeField(_("Purchased Date"),auto_now_add=True)
    isPaid             = models.BooleanField(default=False)
    

    def __str__(self):
        return f"{self.id}-{self.status}"
    

    class Meta:
        ordering = ["-id"]