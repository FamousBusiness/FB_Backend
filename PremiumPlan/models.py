from typing import Iterable
from django.db import models
from users.models import User
from django.utils.translation import gettext_lazy as _
from Phonepe.uniqueID import generate_unique_id





PREMIUM_PLAN_TYPE = [
    ('Trial Period', 'Trial Period'),
    ('One Month Free', 'One Month Free'),
    ('Page Owner', 'Page Owner'),
    ('Ads', 'Ads'),
    ('Bulk Email', 'Bulk Email'),
    ('Bulk Text Message', 'Bulk Text Message'),
    ('Bulk Messenger', 'Bulk Messenger'),
]

PREMIUM_PLAN = [
    ('Trial', 'Trial'),
    ('One Month Free', 'One Month Free'),
    ('Starter', 'Starter'),
    ('Business', 'Business'),
    ('Enterprises', 'Enterprises'),
    ('Silver', 'Silver'),
    ('Gold', 'Gold')
]


PHONEPE_AUTOPAY_TYPE = [
    ('One Month Free', 'One Month Free'),
    ('Paid', 'Paid')
]


PLAN_DURATION = [
    ('Monthly', 'Monthly'),
    ('Yearly', 'Yearly'),
    ('Day', 'Day'),
]


DURATION_PERIOD = [
    ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'),
    ('10', '10'), ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'), ('16', '16'), ('17', '17'),
    ('18', '18'), ('19', '19'), ('20', '20'), ('21', '21'), ('22', '22'), ('23', '23'), ('24', '24'), ('25', '25'), 
    ('26', '26'), ('27', '27'), ('28', '28'), ('29', '29'), ('30', '30'),
]


PLAN_CANCEL_STATUS = [
    ('Approved', 'Approved'),
    ('Cancelled', 'Cancelled'),
]


class PlanDetail(models.Model):
    unique_name         = models.CharField(_("Unique Name"), max_length=50, default='Default')
    name                = models.CharField(choices=PREMIUM_PLAN, max_length=25)
    type                = models.CharField(choices=PREMIUM_PLAN_TYPE, max_length=25,
                                           verbose_name='Marketing Type')
    duration            = models.CharField(choices=PLAN_DURATION, max_length=20, null=True, blank=True, verbose_name='Duration')
    duration_quantity   = models.CharField(max_length=3, blank=True, null=True, choices=DURATION_PERIOD, verbose_name='Duration Length')
    
    tag_line            = models.CharField(max_length=50, null=True, blank=True)
    price               = models.PositiveIntegerField(verbose_name='Plan Price', null=True, blank=True)
    verified            = models.CharField(max_length=300,
                                           verbose_name='Verified Benefits', null=True, blank=True)
    trusted             = models.CharField(max_length=300,
                                           verbose_name='Trusted Benefits', null=True, blank=True)
    trending            = models.CharField(max_length=300,
                                           verbose_name='Trending Benefits', null=True, blank=True)
    authorized          = models.CharField(max_length=300,
                                           verbose_name='Authorized Benefits', null=True, blank=True)
    sponsor             = models.CharField(max_length=300,
                                           verbose_name='Sponsor Benefits', null=True, blank=True)
    super               = models.CharField(max_length=300,
                                           verbose_name='Super Benefits', null=True, blank=True)
    premium             = models.CharField(max_length=300,
                                           verbose_name='Premium Benefits', null=True, blank=True)
    industry_leader     = models.CharField(max_length=300,
                                           verbose_name='Industry Leader Benefits', null=True, blank=True)
    extra_benefits      = models.CharField(max_length=300,
                                           verbose_name='Extra Benefits', null=True, blank=True)
    extra_benefits1     = models.CharField(max_length=300,
                                           verbose_name='Extra Benefits-1', null=True, blank=True)
    

    def __str__(self):
        return f'{self.unique_name} {self.name}'
    

# 
class PremiumPlan(models.Model):
    plan            = models.ForeignKey(PlanDetail, on_delete=models.CASCADE)
    category        = models.ForeignKey('Listings.Category', on_delete=models.CASCADE, null=True)
    lead_view       = models.PositiveIntegerField(default=0, verbose_name='Lead View Quantity')
    job_post        = models.PositiveIntegerField(default=0, verbose_name='Job Post Quantity')
    verified        = models.BooleanField(default=False,     verbose_name='Verified Tag')
    trusted         = models.BooleanField(default=False,     verbose_name='Trusted Tag')
    trending        = models.BooleanField(default=False,     verbose_name='Trending Tag')
    authorized      = models.BooleanField(default=False,     verbose_name='Authorized Tag')
    sponsor         = models.BooleanField(default=False,     verbose_name='Sponsor Tag')
    super           = models.BooleanField(default=False,     verbose_name='Super Tag')
    premium         = models.BooleanField(default=False,     verbose_name='Premium Tag')
    industry_leader = models.BooleanField(default=False,     verbose_name='Industry Leader Tag')
    autopay_payment_type = models.CharField(choices=PHONEPE_AUTOPAY_TYPE, null=True, blank=True, verbose_name="Autopay Payment Type")


    def __str__(self):
        return f"{self.plan.name} Plan for {self.plan.type}"
         


class UserPremiumPlan(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    plan            = models.ForeignKey(PremiumPlan, on_delete=models.SET_NULL, null=True)
    is_paid         = models.BooleanField(default=False)
    is_active       = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add = True, null=True, blank=True)


    def __str__(self):
        return f"{self.user.name}'s {self.plan} plan"
    


class PlanCancelRequest(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    plan            = models.ForeignKey(PremiumPlan, on_delete=models.SET_NULL, null=True)
    approval_status = models.CharField(_("Approval Status"), max_length=50, choices=PLAN_CANCEL_STATUS, null=True, blank=True)


    def __str__(self):
        return f"{self.user.name}\'s Cancellation Request"
    


### Premium Plan Order
class PremiumPlanOrder(models.Model):
    user                   = models.ForeignKey(User, on_delete=models.CASCADE)
    premium_plan           = models.ForeignKey(PremiumPlan, on_delete=models.CASCADE, null=True)
    transaction_id         = models.CharField(_("Transaction ID"), max_length=100, unique=True)
    amount                 = models.PositiveIntegerField(_("Amount"), null=True, blank=False)
    status                 = models.CharField(_("Payment Status"), default="Pending", max_length=254,
        blank=False,
        null=False,
       ) # Pending, Paid, Failed
    details                  = models.CharField(max_length=255, null=True, blank=True)
    purchased_at             = models.DateTimeField(_("Purchased Date"), auto_now_add=True)
    repayment_date           = models.DateTimeField(_("Repayment Date"), null=True, blank=True)
    month_paid               = models.PositiveIntegerField(default=0, null=True, blank=True)
    isPaid                   = models.BooleanField(default=False)
    payment_response         = models.TextField(_("Payment Response"), null=True)
    webhook_response         = models.TextField(_("Webhook Response"), null=True)
    recurring_transaction_id = models.CharField(max_length=40, null=True, blank=True)
    is_active                = models.BooleanField(_("Active"), default=True, null=True, blank=True)
    invoice                  = models.FileField(_("Invoice"), upload_to='PremiumPlanInvoice/', null=True)
    invoice_no               = models.CharField(_("Invoice No"), max_length=30, null=True)
    request_sent             = models.BooleanField(_("Request Sent"), default=False)
    
    
    def __str__(self):
        return f"{self.pk}-{self.status}"
    
    
    class Meta:
        ordering = ["-id"]





# Phonepe Autopay System
class PhonepeAutoPayOrder(models.Model):
    # premium_plan_id          = models.IntegerField(null=True)
    # user_id                  = models.IntegerField(null=True)
    premium_plan_id          = models.ForeignKey(PremiumPlan, on_delete=models.CASCADE, null=True)
    user_id                  = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    merchantUserId           = models.CharField(_("Merchant User ID"), max_length=50, unique=False)
    MerchantSubscriptionId   = models.CharField(_("Merchant Subscription ID"), max_length=50, unique=True) # Sent to phonepe
    subscriptionId           = models.CharField(_("Subscription ID"), max_length=50, unique=True, null=True)  # Received from phonepe
    amount                   = models.IntegerField(_("Amount"))
    authRequestId            = models.CharField(_("Auth Request ID"), max_length=50, unique=True, null=True)
    payment_response         = models.TextField(_("Payment Response"), max_length=2000, null=True)
    webhook_response         = models.TextField(_("Webhook Response"), null=True)
    recurring_transaction_id = models.CharField(max_length=30, null=True, blank=True)
    
    
    def save(self, *args, **kwargs) -> None:
        if not self.MerchantSubscriptionId:
            self.MerchantSubscriptionId = generate_unique_id(PhonepeAutoPayOrder, 'MerchantSubscriptionId')
        if not self.authRequestId:
            self.authRequestId = generate_unique_id(PhonepeAutoPayOrder, 'authRequestId')

        super(PhonepeAutoPayOrder, self).save(*args, **kwargs)
    



class PremiumPlanBenefits(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    plan            = models.ForeignKey(PremiumPlan, on_delete=models.SET_NULL, null=True,  related_name='Premium_Plan_benefits')
    lead_assigned   = models.PositiveBigIntegerField(default=0)
    ads_allowed     = models.PositiveIntegerField(default=0)
    banner_allowed  = models.PositiveIntegerField(default=0)
    jobpost_allowed = models.PositiveIntegerField(default=0)
    is_paid         = models.BooleanField(default=False)
    expired         = models.BooleanField(default=False)
    purchased_at    = models.DateTimeField(_("Purchased Date"), auto_now_add=True)


    def __str__(self):
        return f"{self.user.name} Allowed Benefit List"
    
    class Meta:
        ordering = ["-id"]




class TrialPlanRequest(models.Model):
    user      = models.ForeignKey(User, on_delete=models.CASCADE)
    plan      = models.ForeignKey(PremiumPlan, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(_("Approved"), default=False)
    created_at= models.DateTimeField(auto_now_add=True)
    lead_view = models.PositiveIntegerField(default=0)


    def __str__(self):
        return f"{self.user.name} Trial Plan Request"
    

