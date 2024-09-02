from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from Lead.models import (
    Lead, 
    LeadOrder, ComboLeadOrder
    )
import uuid




#Change the lead status after 5 person purchased
# @receiver(post_save, sender=BusinessPageLeadBucket)
# @receiver(post_save, sender=LeadBucket)
@receiver(post_save, sender=Lead)
def update_lead_status(sender, instance, created, **kwargs):
    if not created:
        lead_id = instance.id
        lead_view = instance.views
        # count_lead_bucket               = LeadBucket.objects.filter(lead_id=lead_id, is_paid=True).count()
        # count_business_page_lead_bucket = BusinessPageLeadBucket.objects.filter(lead_id=lead_id, is_paid=True).count()
        # viewed_lead                     = BusinessPageLeadView.objects.filter(lead_id=lead_id, viewed=True).count()

        # total_assignments = count_lead_bucket + count_business_page_lead_bucket + viewed_lead

        if lead_view >= 5:
            try:
                lead = Lead.objects.get(id=lead_id)
                if not lead.expired:
                    lead.expired = True
                    lead.status = "Completed"
                    lead.save()
                
                # write_total_assignments(lead)
            except ObjectDoesNotExist:
                pass

    else:
        lead_id = instance.id
        lead_view = instance.views
        # count_lead_bucket               = LeadBucket.objects.filter(lead_id=lead_id, is_paid=True).count()
        # count_business_page_lead_bucket = BusinessPageLeadBucket.objects.filter(lead_id=lead_id, is_paid=True).count()
        # viewed_lead                     = BusinessPageLeadView.objects.filter(lead_id=lead_id, viewed=True).count()

        # total_assignments = count_lead_bucket + count_business_page_lead_bucket + viewed_lead

        if lead_view >= 5:
            try:
                lead = Lead.objects.get(id=lead_id)
                if not lead.expired:
                    lead.expired = True
                    lead.status = "Completed"
                    lead.save()
                # write_total_assignments( lead)
            except ObjectDoesNotExist:
                pass

# def write_total_assignments(lead):
#     with open('total_assignment.txt', 'w') as file:
#         file.write(str(lead))
            


#Generate Unique Transaction Id for Every Lead Order
@receiver(pre_save, sender=LeadOrder)
def generate_unique_transaction_id(sender, instance, **kwargs):
    if not instance.transaction_id:
        unique_id = str(uuid.uuid4().hex)[:40]
        instance.transaction_id = unique_id

        while sender.objects.filter(transaction_id=instance.transaction_id).exists():
            instance.transaction_id = str(uuid.uuid4().hex)[:40]

pre_save.connect(generate_unique_transaction_id, sender=LeadOrder)




#Generate Unique Transaction ID for Combo Lead Order
@receiver(pre_save, sender=ComboLeadOrder)
def generate_unique_transaction_id(sender, instance, **kwargs):
    if not instance.transaction_id:
        unique_id = str(uuid.uuid4().hex)[:40]
        instance.transaction_id = unique_id

        while sender.objects.filter(transaction_id=instance.transaction_id).exists():
            instance.transaction_id = str(uuid.uuid4().hex)[:40]

pre_save.connect(generate_unique_transaction_id, sender=LeadOrder)

