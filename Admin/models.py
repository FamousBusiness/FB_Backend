from django.db import models
from users.models import User
from django.utils.translation import gettext_lazy as _
from PremiumPlan.models import PremiumPlan








class AutoPayRequestSent(models.Model):
    user            = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    transaction_id  = models.CharField(_("Transaction ID"), max_length=30)
    premium_plan    = models.ForeignKey(PremiumPlan, on_delete=models.SET_NULL, null=True)
    phonepe_response = models.TextField(null=True)
    amount           = models.IntegerField(default=0)
    subscriptionID   = models.CharField(_("Phonepe SubScription ID"), max_length=40)
    is_sent          = models.BooleanField(_("Success"), default=False)
    message          = models.CharField(_("Message"), max_length=30)
    sent_date        = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f'{self.user} Autopay Request'




class AutoPaySuccessResponse(models.Model):
    user             = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    transaction_id   = models.CharField(_("Transaction ID"), max_length=30)
    premium_plan     = models.ForeignKey(PremiumPlan, on_delete=models.SET_NULL, null=True)
    phonepe_response = models.TextField(null=True)
    subscriptionID   = models.CharField(_("Phonepe SubScription ID"), max_length=40, null=True)
    is_success       = models.BooleanField(_("Success"), default=False)
    message          = models.CharField(_('Message'), max_length=40, null=True)
    created_date     = models.DateTimeField(auto_now_add=True, null=True)
    status           = models.CharField(_("Status"), max_length=15, null=True)

    def __str__(self):
        return f'{self.user} Webhook Response'
