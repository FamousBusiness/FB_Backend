from django.dispatch import receiver
from django.db.models.signals import pre_save
from datetime import timedelta
from django.utils import timezone
from ADS.models import ADS




#Have to use celery beat to perform this task
# @receiver(pre_save, sender=ADS)
# def set_expired(sender, instance, **kwargs):
#     if not instance.is_active and instance.start_time:
#         current_time = timezone.now()
#         if current_time - instance.start_time >= timedelta(days=10):
#             instance.is_active = False

            
