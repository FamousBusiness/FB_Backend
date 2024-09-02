from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from email.utils import formataddr
from django.template.loader import render_to_string
from django.utils.html import strip_tags


 
            
            
@shared_task
def send_trial_plan_request_mail_to_admin(data):
    
    plain_message = f"{data['user_name']} Raised a request for Trial Plan"
    business_email = 'sales@famousbusiness.in'
    sender_name    = 'Famous Business'
    sender_email   =  'customercare@famousbusiness.in'
    sender         = formataddr((sender_name, sender_email))

    message = EmailMultiAlternatives(
        subject = 'New Trial Plan Request Raised',
        body = plain_message,
        from_email = sender,
        to= [business_email]
            )

    message.send()




@shared_task
def premium_plan_purchase_mail(data):
    html_message = render_to_string("../templates/mail/premiumplan.html", {
        'business_owner_name' : data['business_name'],
        'transaction_id': data['transaction_id'],
        'business_mail': data['business_mail'],
        'amount': data['amount']
    })

    plain_message  = strip_tags(html_message)
    sender_name    = 'Famous Business'
    sender_email   = 'customercare@famousbusiness.in'
    sender         = formataddr((sender_name, sender_email))

    message = EmailMultiAlternatives(
            subject = 'Famous Business Plan Payment Notification', 
            body = plain_message,
            from_email = sender,
            to= [data['business_mail']]
                )

    message.attach_alternative(html_message, "text/html")
    message.send()



@shared_task
def send_trial_plan_activation_mail(data):
    html_message = render_to_string("../templates/Admin/trial_plan_activation.html", {
        'business_mail': data['business_mail'],
        'lead_view': data['lead_view_quantity'],
        'business_name': data['business_name']
    })

    plain_message  = strip_tags(html_message)
    sender_name    = 'Famous Business'
    sender_email   = 'customercare@famousbusiness.in'
    sender         = formataddr((sender_name, sender_email))

    message = EmailMultiAlternatives(
            subject = 'Free Plan Activation Notification', 
            body = plain_message,
            from_email = sender,
            to= [data['business_mail']]
                )

    message.attach_alternative(html_message, "text/html")
    message.send()



