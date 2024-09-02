from celery import shared_task
from django.core.mail import EmailMultiAlternatives
# from django.utils.html import strip_tags




@shared_task
def send_mail_to_company_job_post(data):

    # html_message = render_to_string("../templates/mail/business_lead_mail.html/", {
    #     'business_owner_name' : data['business']["business_name"],
    #     'client_name'         : data['lead_name'],
    #     'client_mobile_number': data['lead_mobile_number'],
    #     'client_requirements' : data['lead_requirements']
    # })

    # plain_message = strip_tags(html_message)
    message = f"""Dear {data['business_name']}, 
                 You have Posted a job of {data['job_position']} in {data['joblocation']}"""
    
    message = EmailMultiAlternatives(
            subject = 'Elevate Your Business with Exclusive PAN India Leads', 
            body = message,
            from_email = 'customercare@famousbusiness.in' ,
            to= [data['mail']]
                )

    # message.attach_alternatiwve(html_message, "text/html")
    message.send()


@shared_task
def send_mail_to_company_apply_job(data):
    print(data['business_email'])
    
    message = f"""Dear {data['business_name']}, 
                 Mr.{data['candidate_first_name']} '' {data['candidate_last_name']} Applied job in {data['job_position']} in {data['joblocation']}"""
   
    message = EmailMultiAlternatives(
            subject = 'Job Application from Famous Business', 
            body = message,
            from_email = 'customercare@famousbusiness.in' ,
            to= [data['business_email']]
                )

    message.send()


@shared_task
def send_mail_to_candidate_apply_job(data):

    message = f"""Dear Mr.{data['candidate_first_name']} '' {data['candidate_last_name']}, 
                 You have Successfully Applied job for {data['job_position']} in {data['business_name']}"""
    # print(data['candidate_mail'])
    message = EmailMultiAlternatives(
            subject = 'Job Applied in Famous Business', 
            body = message,
            from_email = 'customercare@famousbusiness.in' ,
            to= [data['candidate_mail']]
                )

    message.send()