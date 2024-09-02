from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.template.loader import render_to_string


@shared_task(rate_limit='14/s')
def send_test_email(data):

    html_message = render_to_string("../templates/mail/normal_email.html", {
        'business_owner_name' : data['business_name'],
        'customer_name': data['customer_name'],
        'location': data['location'],
        'requirements': data['requirements']
    })

    plain_message = strip_tags(html_message)

    message = EmailMultiAlternatives(
            subject = 'Your Business Page is live now', 
            body = plain_message,
            from_email = 'customercare@famousbusiness.in' ,
            to= [data['email']]
                )
    
    message.attach_alternative(html_message, "text/html")
    message.send()




@shared_task(rate_limit='14/s')
def send_manual_mail(data):
    
    for business_data in data:
        pass