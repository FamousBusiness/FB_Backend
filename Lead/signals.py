from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from Lead.models import (
    Lead, CategoryLeadViewQuantity,
    LeadOrder, ComboLeadOrder
    )
import uuid




##### Update Lead to Expired if Crosses Limit
@receiver(post_save, sender=Lead)
def update_lead_status(sender, instance, created, **kwargs):
    if not created:
        lead_id       = instance.id
        lead_category = instance.category
        lead_view     = instance.views

        try:
            assigned_lead_view_quantity = CategoryLeadViewQuantity.objects.get(category = lead_category)

            if lead_view >= assigned_lead_view_quantity.quantity:
                try:
                    lead = Lead.objects.get(id=lead_id)

                    if not lead.expired:
                        lead.expired = True
                        lead.status = "Completed"
                        lead.save()
                    
                except ObjectDoesNotExist:
                    pass
        except Exception as e:
            assigned_lead_view_quantity = 5

            if lead_view >= assigned_lead_view_quantity:
                try:
                    lead = Lead.objects.get(id=lead_id)

                    if not lead.expired:
                        lead.expired = True
                        lead.status = "Completed"
                        lead.save()
                    
                except ObjectDoesNotExist:
                    pass

    else:
        lead_id       = instance.id
        lead_view     = instance.views
        lead_category = instance.category

        try:
            assigned_lead_view_quantity = CategoryLeadViewQuantity.objects.get(category = lead_category)

            if lead_view >= assigned_lead_view_quantity.quantity:
                try:
                    lead = Lead.objects.get(id=lead_id)

                    if not lead.expired:
                        lead.expired = True
                        lead.status = "Completed"
                        lead.save()
                    # write_total_assignments( lead)
                except ObjectDoesNotExist:
                    pass
        except Exception as e:
            assigned_lead_view_quantity = 5

            if lead_view >= assigned_lead_view_quantity:
                try:
                    lead = Lead.objects.get(id=lead_id)

                    if not lead.expired:
                        lead.expired = True
                        lead.status = "Completed"
                        lead.save()
                    # write_total_assignments( lead)
                except ObjectDoesNotExist:
                    pass

            


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

