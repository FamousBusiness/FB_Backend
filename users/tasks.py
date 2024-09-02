from celery import shared_task
from django.core.mail import send_mail, EmailMessage
from IFBD_Project import settings
from django.conf import settings
from twilio.rest import Client
from celery import Task
from django.template.loader import render_to_string




# class Utils:
#     @staticmethod
#     def send_mail_password_reset(data):
#         email = EmailMessage(
#             subject=data['subject'],
#             body= data['body'],
#             from_email='customercare@famousbusiness.in',
#             to=[data['to_email']]
#         )

#         email.send()

class Utils:
     @staticmethod
     def send_mail_password_reset(data):
          send_mail(
               subject=data['subject'],
               message=data['body'],
               from_email='customercare@famousbusiness.in',
               recipient_list=[data['to_email']],
               fail_silently=True
          )



@shared_task()
def send_mail_to_business(to_email):
        mail_subject = "Business Created from IFBD"
        message = "Your Business has been created please click on the link to get the access"
        html_content = render_to_string('../templates/mail/send_mail.html')
        html_message = f'''
                     {html_content}
                     '''

        send_mail(
            subject = mail_subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[to_email],
            fail_silently=True,
            
        )



@shared_task()
def send_otp_via_message(mobile_number,otp):     
    client= Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
    message=client.messages.create(
        body=f'your otp is:{otp}',
        from_=f'{settings.TWILIO_PHONE_NUMBER}',
        to=f'{settings.COUNTRY_CODE}{mobile_number}'
        )
    


@shared_task()
def send_otp_via_whatsapp(mobile_number,otp):     
    client= Client(settings.ACCOUNT_SID,settings.AUTH_TOKEN)
    message=client.messages.create(
        body=f'your otp is:{otp}',
        from_=f'{settings.TWILIO_WHATSAPP_NUMBER}',
        to=f'whatsapp:{settings.COUNTRY_CODE}{mobile_number}'
        )

   