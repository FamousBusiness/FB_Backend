from celery import shared_task
from django.core.mail import send_mail
from IFBD_Project import settings
from django.conf import settings
from twilio.rest import Client
from celery import Task




@shared_task()
def send_message(mobile_number,url, message):     
    client= Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
    message=client.messages.create(
        body=f'{message} {url}',

        from_=f'{settings.TWILIO_PHONE_NUMBER}',
        
        to=f'{settings.COUNTRY_CODE}{mobile_number}'
        )
