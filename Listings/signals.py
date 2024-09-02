from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from users.models import User
from Listings.models import (Business, 
    )






#when a User deletes it will automatically delete its related business page
@receiver(post_delete, sender=User)
def delete_related_business(sender, instance, **kwargs):
    Business.objects.filter(owner=instance).delete()




#Changes users model mobile number According to the Business Mobile Number
@receiver(post_save, sender=Business)
def update_user_from_business(sender, instance,created, **kwargs):
    if not created:
        user = instance.owner
        user.email = instance.email
        user.mobile_number = instance.mobile_number
        user.save()
            
    if created:
        user = instance.owner
        user.email = instance.email
        user.mobile_number = instance.mobile_number
        user.save()


