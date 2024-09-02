from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import SoftwareOrder
import uuid




@receiver(pre_save, sender=SoftwareOrder)
def generate_unique_transaction_id(sender, instance, **kwargs):
    if not instance.transaction_id:
        unique_id = str(uuid.uuid4().hex)[:40]
        instance.transaction_id = unique_id

        while sender.objects.filter(transaction_id=instance.transaction_id).exists():
            instance.transaction_id = str(uuid.uuid4().hex)[:40]

pre_save.connect(generate_unique_transaction_id, sender=SoftwareOrder)

