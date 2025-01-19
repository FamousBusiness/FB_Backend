from django.db import models
from users.models import User
from django.utils.translation import gettext_lazy as _


WITHDRAWAL_STATUS = (
    ('Success', 'Success'),
    ('Pending', 'Pending'),
    ('Cancelled', 'Cancelled'),
    ('Rejected', 'Rejected'),
)

TRANSACTION_MODE = (
    ('Add', 'Add'),
    ('Transfer', 'Transfer'),
    ('Order', 'Order'),
)


ADDMONEY_FEE = [
    ('PG Fee', 'PG Fee'),
    ('Platform Fee', 'Platform Fee'),
]


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


class AddMoneyFee(models.Model):
    name       = models.CharField(_("Fee Name"), choices=ADDMONEY_FEE, max_length=15)
    percentage = models.PositiveIntegerField(_("Percentage"), default=1)


    def __str__(self):
        return f'Addmoney {self.name}'
    


class TransferMoneyFee(models.Model):
    name       = models.CharField(_("Fee Name"), choices=ADDMONEY_FEE, max_length=15)
    percentage = models.PositiveIntegerField(_("Percentage"), default=1)


    def __str__(self):
        return f'Transfer Money {self.name}'

    


class Transaction(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id  = models.CharField(_('Transaction ID'), max_length=35)
    date_created    = models.DateTimeField(_("Date Created"), auto_now_add=True)
    amount          = models.PositiveIntegerField(_('Transaction Amount'), default=0)
    currency        = models.CharField(_("Currency"), default='INR')
    status          = models.CharField(_("Status"), max_length=20, null=True)
    is_completed    = models.BooleanField(_("Completed"), default=False)
    is_settled      = models.BooleanField(_("Settlement"), default=False)
    mode            = models.CharField(_("Payment Mode"), choices=TRANSACTION_MODE, max_length=15, null=True)
    receiver        = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='receiver')
    ad_money_fee    = models.ManyToManyField(AddMoneyFee)
    transfer_fee    = models.ManyToManyField(TransferMoneyFee)


    def __str__(self):
        return f'{self.user} Transaction'
    
    class Meta:
        ordering = ['-id']
    


### User Bank Account
class UserBankAccount(models.Model):
    user               = models.ForeignKey(User, on_delete=models.CASCADE)
    acc_holder_name    = models.CharField(_('Account Holder Name'), max_length=30)
    acc_holder_address = models.CharField(_("Account Holder Address"), max_length=100)
    acc_number         = models.CharField(_("Account Number"), max_length=20)
    ifsc_code          = models.CharField(_('IFSC Code'), max_length=15)
    bank_name          = models.CharField(_("Bank Name"), max_length=30)
    bank_address       = models.CharField(_("Bank Address"), max_length=100)
    additional_info    = models.CharField(_("Additional Info"), max_length=100, null=True)
    doc                = models.FileField(upload_to='UserBankDoc/', null=True)


    def __str__(self):
        return f"{self.user} Bank Account"
    
    class Meta:
        ordering = ['-id']





class Withdrawals(models.Model):
    user         = models.ForeignKey(User, on_delete=models.CASCADE)
    amount       = models.PositiveIntegerField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    reference_id = models.CharField(_("Reference ID"), max_length=35)
    bank         = models.ForeignKey(UserBankAccount, on_delete=models.CASCADE)
    status       = models.CharField(max_length=15, default='Pending', choices=WITHDRAWAL_STATUS)
    is_completed = models.BooleanField(_("Completed"), default=False)


    def __str__(self):
        return f'{self.user} Withdrawal Request'
    
    class Meta:
        ordering = ['-id']


    



class PhonpeWalletOrder(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    amount          = models.PositiveIntegerField(_("Amount"), default=0)
    transaction_id  = models.CharField(_("Transaction ID"), max_length=40)
    purpose         = models.CharField(_("Purpose"), max_length=15)
    phoepe_response = models.TextField(_("Phonepe Response"), null=True)
    created_at      = models.DateTimeField(_("Created Date"), auto_now_add=True)


    def __str__(self):
        return f"Phonepe order {self.pk}"
    


    
    
    



