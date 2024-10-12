from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from PremiumPlan.models import PlanCancelRequest, PremiumPlanOrder, PremiumPlanBenefits
from django.db import transaction
import uuid
from datetime import timedelta
from django.utils import timezone





#When admin approve the Cancellation Request this
#Signal will execute and null the every value
@receiver(post_save,sender=PlanCancelRequest)
def plan_cancellation_approval(sender, instance, **kwargs):
    
    if instance.approval_status == 'Approved':
        # print(instance.approval_status)
        with transaction.atomic():
            user_premium_plan = PremiumPlanBenefits.objects.get(user=instance.user, plan=instance.plan)
            user_premium_plan.expired = True
            user_premium_plan.save()

            assigned_benefits = PremiumPlanBenefits.objects.get(user=instance.user, plan=instance.plan)
            assigned_benefits.lead_assigned = 0
            assigned_benefits.jobpost_allowed = 0
            assigned_benefits.ads_allowed = 0
            assigned_benefits.banner_allowed = 0
            assigned_benefits.is_paid = False
            assigned_benefits.save()




#Generate Unique Transaction ID for Every Order
@receiver(pre_save, sender=PremiumPlanOrder)
def generate_unique_transaction_id(sender, instance, **kwargs):
    if not instance.transaction_id:
        unique_id = str(uuid.uuid4().hex)[:40]
        instance.transaction_id = unique_id

        while sender.objects.filter(transaction_id=instance.transaction_id).exists():
            instance.transaction_id = str(uuid.uuid4().hex)[:40]

pre_save.connect(generate_unique_transaction_id, sender=PremiumPlanOrder)





# Expire the premium plans after the period ends
# @receiver(post_save, sender=PremiumPlanBenefits)
# def check_user_premium_plan_duration(sender, instance, created, **kwargs):
#     if not created:  
#         premium_plan = instance.plan.plan
#         duration = premium_plan.duration
#         duration_length = premium_plan.duration_quantity

#         if duration == 'Monthly':
#             time_to_check = timedelta(days=30 * int(duration_length))
#         elif duration == 'Yearly':
#             time_to_check = timedelta(days=365 * int(duration_length))
#         else:
#             time_to_check = timedelta(days=1 * int(duration_length))

#         now = timezone.now()

#         if now - instance.purchased_at > time_to_check:
#             instance.lead_assigned = 0
#             instance.jobpost_allowed = 0
#             instance.ads_allowed = 0
#             instance.banner_allowed = 0
#             instance.expired = True

#             instance.save()



