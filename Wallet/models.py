from django.db import models
from users.models import User
from django.utils.translation import gettext_lazy as _





class Wallet(models.Model):
    user     = models.OneToOneField(User, on_delete=models.CASCADE)
    balance  = models.PositiveIntegerField(_("Wallet Balance"), default=0)
    currency = models.CharField(_("Currency"), default='INR', max_length=5)


    def __str__(self):
        return f'{self.user} Wallet'


class MatureWallet(models.Model):
    user     = models.OneToOneField(User, on_delete=models.CASCADE)
    balance  = models.PositiveIntegerField(_("Wallet Balance"), default=0)
    currency = models.CharField(_("Currency"), default='INR', max_length=5)


    def __str__(self):
        return f'{self.user} Wallet'
    

class ImmatureWallet(models.Model):
    user     = models.OneToOneField(User, on_delete=models.CASCADE)
    balance  = models.PositiveIntegerField(_("Wallet Balance"), default=0)
    currency = models.CharField(_("Currency"), default='INR', max_length=5)


    def __str__(self):
        return f'{self.user} Wallet'
    

    



class Transaction(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id  = models.UUIDField(_('Transaction ID'))
    date_created    = models.DateTimeField(_("Date Created"), auto_now_add=True)
    amount          = models.PositiveIntegerField(_('Transaction Amount'), default=0)
    currency        = models.CharField(_("Currency"), default='INR')
    fee             = models.PositiveIntegerField(_("Transaction Fee"), default=0)
    payout_balance  = models.PositiveIntegerField(_("Payout Balance"), default=0)


    def __str__(self):
        return f'{self.user} Transaction'
    



