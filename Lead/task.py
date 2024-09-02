from celery import shared_task
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from email.utils import formataddr
import requests
from celery import group
from Lead.models import Lead
from Listings.models import Business
from django.utils import timezone



@shared_task
def send_business_page_lead_mail(data):

    html_message = render_to_string("../templates/mail/business_lead_mail.html/", {
        'business_owner_name' : data['business']["business_name"],
        'client_name'         : data['lead_name'],
        'client_mobile_number': data['lead_mobile_number'],
        'client_requirements' : data['lead_requirements']
    })
    plain_message = strip_tags(html_message)

    sender_name  = 'Famous Business'
    sender_email = 'customercare@famousbusiness.in'
    sender       = formataddr((sender_name, sender_email))
    
    message = EmailMultiAlternatives(
        subject = 'Elevate Your Business with Exclusive PAN India Leads', 
        body = plain_message,
        # body = 'plain_message',
        from_email = sender,
        to= [data['business']["email"], 'arshadiqbal9871@gmail.com']
            )

    message.attach_alternative(html_message, "text/html")
    message.send()




@shared_task
def send_lead_mail_to_category_wise_business(data):
   
    for business_data in data:
        business_email = business_data.get('business_email')
        business_name  = business_data.get('business_name')
        customer_name  = business_data.get('customer_name', '')
        location       = business_data.get('location', '')
        requirements   = business_data.get('requirements', '')

        html_message = render_to_string("../templates/mail/lead_mail.html/", {
            'business_owner_name' : business_name,
            'customer_name': customer_name,
            'location': location,
            'requirements': requirements,
        })
        plain_message = strip_tags(html_message)
        
        # to_emails = ', '.join(data['business_email'])

        sender_name  = 'Famous Business'
        sender_email =  'customercare@famousbusiness.in'
        sender       = formataddr((sender_name, sender_email))

        message = EmailMultiAlternatives(
            subject = 'Elevate Your Business with Exclusive PAN India Leads', 
            body = plain_message,
            from_email = sender,
            to= [business_email]
                )

        message.attach_alternative(html_message, "text/html")
        message.send()



@shared_task()
def send_category_wise_business_mail_excel_upload(data):
    
    for business_data in data:
        business_email = business_data.get('business_email')
        business_name  = business_data.get('business_name')
        customer_name  = business_data.get('customer_name', '')
        location       = business_data.get('location', '')
        requirements   = business_data.get('requirements', '')

        html_message = render_to_string("../templates/mail/lead_mail.html/", {
            'business_owner_name' : business_name,
            'customer_name': customer_name,
            'location': location,
            'requirements': requirements,
        })

        plain_message = strip_tags(html_message)
        # to_emails = ', '.join(data['business_email'])
        sender_name  = 'Famous Business'
        sender_email = 'customercare@famousbusiness.in'
        sender       = formataddr((sender_name, sender_email))

        message = EmailMultiAlternatives(
            subject = f'New Customer Inquiry - {requirements}',
            body = plain_message,
            from_email = sender,
            to= [business_email]
                )

        message.attach_alternative(html_message, "text/html")
        message.send()




@shared_task
def send_category_wise_business_message_excel_upload(data):
    for business_data in data:
        url           = "http://trans.smsfresh.co/api/sendmsg.php"
        mobile_number = business_data.get('mobile_number') 

        params = {
                "user": 'WEBZOTICAPROMO',
                "pass": '123456',
                "sender": 'WBFSPL',
                "phone": mobile_number,

                "text": "New%20Lead%20has%20been%20assign%20for%20your%20Business.%0A%20Please%20Share%20the%20Quotation.              %0A%20Regards%2C%20WFBSPL%20famousbusiness.in%0A%209871475373",

                "priority": 'ndnd',
                "stype": 'normal'
            }
        
        response = requests.get(url, params=params)

        response_data = {
            "status-code": response.status_code
        }

        return response_data
        # return response


@shared_task
def send_category_wise_business_whatsapp_message_lead_excel_upload(data):
    for business_data in data:
        api_url = "https://bhashsms.com/api/sendmsg.php"
        mobile_number = business_data.get('mobile_number') 
        business_name  = business_data.get('business_name')
        customer_name  = business_data.get('customer_name', '')
        requirements   = business_data.get('requirements', '')

        params = {
            "user" : "WEBZOTICA",
            "pass" : "123456",
            "sender" : "BUZWAP",
            "phone" : mobile_number,
            "text": "final_001",
            "priority" : "wa",
            "stype" : "normal",
            "Params": f"{business_name}, {customer_name}, {requirements}",
            "htype" : "image",
            "imageUrl" : "https://mdwebzotica.famousbusiness.in/Lead_image_black_blue.jpg"
        }

        url = f"{api_url}?user={params['user']}&pass={params['pass']}&sender={params['sender']}&phone={params['phone']}&text={params['text']}&priority={params['priority']}&stype={params['stype']}&htype={params['htype']}&url={params['imageUrl']}"

        response = requests.get(url, params=params)

        response_data = {
            "status-code": response.status_code
        }

        return response_data

       




@shared_task
def send_mail_for_remaining_combo_lead(data):

    plain_message = f"Dear User {data['remaining_lead']} will be sent to you shortly"

    sender_name  = 'Famous Business'
    sender_email =  'customercare@famousbusiness.in'
    sender       = formataddr((sender_name, sender_email))

    message = EmailMultiAlternatives(
        subject= "Bulk Lead Purchase Notification",
        body=plain_message,
        from_email=sender,
        to= [data['email'], 'sahooranjitkumar53@gmail.com']   
    )
    # print(data['email'])
    # print(data['remaining_lead'])
    message.send()




@shared_task
def Lead_purchase_mail(data):
    html_message = render_to_string("../templates/mail/lead_purchased.html", {
        'name' : data['name'],
        'transaction_id': data['transaction_id'],
        'email': data['email'],
        'amount': data['amount']
    })

    plain_message  = strip_tags(html_message)
    sender_name    = 'Famous Business'
    sender_email   = 'customercare@famousbusiness.in'
    sender         = formataddr((sender_name, sender_email))

    message = EmailMultiAlternatives(
            subject = 'Famous Business Lead Payment Notification', 
            body = plain_message,
            from_email = sender,
            to= [data['email']]
                )

    message.attach_alternative(html_message, "text/html")
    message.send()





@shared_task
def beat_task_to_send_lead_mail_every_10_minute():
    current_date = timezone.now().date()
    current_month = current_date.month
    current_year  = current_date.year
    
    leads = Lead.objects.filter(
        created_at__date=current_date, 
        created_at__month=current_month,
        created_at__year=current_year,
        mail_sent=False,
        category_lead=False
        )
    
    tasks = []

    for lead in leads:
        business_pages = Business.objects.filter(category=lead.category, city=lead.city).values('email','business_name', 'mobile_number')

        for business in business_pages:
            data = [{
                        'business_email': business["email"],
                        'business_name': business["business_name"],
                        'location': lead.city, 
                        'customer_name': lead.created_by,
                        'requirements': lead.requirement, 
                        'mobile_number': business["mobile_number"]
            } ]

            # tasks.append(send_category_wise_business_mail_excel_upload.s(data))
            tasks.append(send_category_wise_business_message_excel_upload.s(data))
            tasks.append(send_category_wise_business_whatsapp_message_lead_excel_upload.s(data))

        lead.mail_sent = True
        lead.save()

        break

    group(*tasks).apply_async()



        
