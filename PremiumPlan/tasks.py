from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from email.utils import formataddr
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import requests


 
            
            
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




#### Send Invoice of Premium Plan First Time Purchase
@shared_task
def send_premium_plan_first_invoice(data):
    api_url = "https://bhashsms.com/api/sendmsg.php"

    mobile_number = data['mobile_number']
    document_name = data['document_name']

    params = {
        "user" : "WEBZOTICA",
        "pass" : "123456",
        "sender" : "BUZWAP",
        "phone" : mobile_number,
        "text": "plan_invoice", 
        "priority" : "wa",
        "stype" : "normal",
        # "Params": "1",
        "htype" : "document",
        "imageUrl" : f"https://mdwebzotica.famousbusiness.in/{document_name}"
    }

    url = f"{api_url}?user={params['user']}&pass={params['pass']}&sender={params['sender']}&phone={params['phone']}&text={params['text']}&priority={params['priority']}&stype={params['stype']}&htype={params['htype']}&url={params['imageUrl']}"

    response = requests.get(url, params=params)
    response.raise_for_status() 

    return {
            "status_code": response.status_code,
            "response_text": response.text
        }





