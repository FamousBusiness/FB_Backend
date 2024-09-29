from email.utils import formataddr
from celery import shared_task, Task
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
import requests
from Listings.models import Business
import pandas as pd
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from users.models import User
from Listings.models import (
    Business, Category, SubCategory, BusinessEmailID, 
    BusinessMobileNumbers, ProductService
                             )
from Brands.models import BrandBusinessPage
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
import time
import hashlib
from django.db.models import Q
from rest_framework.response import Response
from django.db import IntegrityError
import re
from django.utils.html import strip_tags
from celery.exceptions import MaxRetriesExceededError
import time





#Send mail to Business owner
#To Land them on profile page
# @shared_task()
# def send_email(data):
#    print(data['name'])
#    print(data['to_email'])
#    subject = data['subject']
#    message = "<h1>Your Business Page is live now</h1>"
#    email_from = 'customercare@famousbusiness.in'
#    recipient_list = [data['to_email']]
#    html_content = render_to_string('../templates/mail/normal_email.html', {'business_id': data['name']})
#    html_message = f'''
#                     {html_content}
#                      '''
#    send_mail(subject, message, email_from, recipient_list, html_message=html_message )   




# @shared_task
@shared_task(rate_limit='14/s', bind=True, max_retries=0)
def send_email(self,data):

    try:
        # # for business_data in data:
        #     business_email = business_data.get('to_email')
        #     link           = business_data.get('link')
        #     business_name  = business_data.get('business_name')
            business_email = data["to_email"]
            link           = data["link"]
            business_name  = data["business_name"]

            html_message = render_to_string("../templates/mail/welcome_mail.html/", {
                'link': link,
                'business_owner_name' : business_name
            })
            
            plain_message = strip_tags(html_message)
            sender_name  = 'Famous Business'
            sender_email = 'customercare@famousbusiness.in'
            sender       = formataddr((sender_name, sender_email))
            
            message = EmailMultiAlternatives(
                    subject = 'Your Business Page is live now', 
                    body = plain_message,
                    from_email = sender,
                    to= [business_email]
                        )
            
            message.attach_alternative(html_message, "text/html")
            message.send(fail_silently=True)
          

    except Exception as e:
        print(f"Failed to send email to {business_email}. Error: {str(e)}")

    print("Finished sending emails")


    


@shared_task
def process_excel_file(excel_file_path):
        try:
            df = pd.read_excel(excel_file_path)
            df = df.fillna('')
        except Exception as e:
            print(f"Error during Excel parsing: {str(e)}")
            # return HttpJsonResponse('error: Failed to Parse the file')
            return {'msg': 'error: Failed to Parse the file'}

        skipped_business_names = []
        existing_user = []
        skipped_numbers = []

        for index, row in df.iterrows():
            try:
                # with transaction.atomic():

                try:
                    email_id = str(row['E-mail ID'])
                    email_ids = [email_id.strip() for part in re.split(r'[,/]', email_id) for email_id in part.split(',')]

                    email_ids = list(filter(None, email_ids))
                    if email_ids:
                        first_email_id = email_ids[0]
                    else:
                        first_email_id = None

                except Exception as e:
                    # return HttpJsonResponse(f"Error while detecting the mail ID: {str(e)}")
                    return {'msg': f"Error while detecting the mail ID: {str(e)}"}


                    
                try:
                    mobile_number_raw     = row.get('Mobile No', '')

                    if not mobile_number_raw:
                        continue

                    try:
                        filter_mobile_No  = str(mobile_number_raw)
                        comma_separated   = [mobile_No.strip() for part in re.split(r'[,/]', filter_mobile_No) for mobile_No in part.split(',')]
                        mobile_number_raw = comma_separated[0]

                    except Exception as e:
                        return {'msg': f"Mobile Number is not in proper format {str(e)}"}

                    # if not mobile_number_raw:
                    #     #  return HttpJsonResponse("Dont left any blank mobile number field")
                    #     return {'msg': 'Dont left any blank mobile number field'}
                    
                    if mobile_number_raw and len(str(mobile_number_raw)) > 15:
                        skipped_numbers.append(mobile_number_raw)
            
                    if isinstance(mobile_number_raw, str):
                        mobile_number = int(mobile_number_raw) if mobile_number_raw.isdigit() else None
                    elif isinstance(mobile_number_raw, int):
                        mobile_number = mobile_number_raw
                    else:
                        mobile_number = None

                except:
                    # return HttpJsonResponse(f"""Please provide a valid mobile number(Number Should be less than 12 Digit) and 
                    #        donot left blank space While Uploading the Mobile Number in row {index + 2}:{','.join(map(str, skipped_numbers))}""")
                    return {'msg': 'Mobile Number Issue'}
                    
                try:
                    category_type     = row.get('Category', '')
                    established_on_raw= row.get('Year of Establishment', '')
                    established_on    = int(established_on_raw) if established_on_raw.isdigit() else None
                    business_name     = row.get('Business Name', '')
                    email             = first_email_id
                    state             = row.get('State', '')
                    city              = row.get('City', '')
                    pincode           = row.get('Pin', '')
                    Director          = row.get('Director', '')
                    About_my_Business = row.get('About my Business', '')
                    Product_Service   = row.get('Product & Service', '')
                    Search            = row.get('Search', '')
                    Website           = row.get('Website', '')
                    Address           = row.get('Address', '')

                except Exception as e:
                    # return HttpJsonResponse(f"Error While getting the value from excel data: {str(e)}")
                    return {'msg': f"Error While getting the value from excel data: {str(e)}"}
                    

                try:
                    CIN_No                = row.get('CIN_No', business_name)
                    GSTIN                 = row.get('GSTIN', business_name)
                    DIN                   = row.get('DIN', business_name)
                    Company_No            = row.get('Company_No', business_name)
                    RoC                   = row.get('RoC', '')

                except Exception as e:
                    # return HttpJsonResponse(f"Error while fetching the CIN, DIN, GSTIN, Company_No, WhatsApp and RoC: {str(e)}")
                    return {'msg': f"Error while fetching the CIN, DIN, GSTIN, Company_No, WhatsApp and RoC: {str(e)}"}
                    
                try:
                    whatsapp_number_raw = row.get('Whatsapp', '')
                    # whatsapp_number = row.get('Whatsapp', '')

                    if isinstance(whatsapp_number_raw, str):
                        whatsapp_number = int(whatsapp_number_raw) if whatsapp_number_raw.isdigit() else None
                    elif isinstance(whatsapp_number_raw, int):
                        whatsapp_number = whatsapp_number_raw
                    else:
                        whatsapp_number = None
                        
                    if whatsapp_number and len(str(whatsapp_number)) > 15:
                        skipped_numbers.append(whatsapp_number)
                        #  return HttpJsonResponse(f'Error: Whatsapp number in row {index + 2} has more than 15 digit')
                        return {'msg': f'Error: Whatsapp number in row {index + 2} has more than 15 digit'}

                except Exception as e:
                    # return HttpJsonResponse(f'Error while getting whatsapp number value: {str(e)}' )
                    return {'msg': f'Error while getting whatsapp number value: {str(e)}'}
                    
                try:
                    user = User.objects.filter(
                              Q(mobile_number=mobile_number) | 
                              Q(email=first_email_id) | 
                              Q(business_name=business_name) | 
                              Q(name=business_name)
                              ).first()

                    if not user:
                        user, created = User.objects.get_or_create(
                            email=email,
                            mobile_number=mobile_number,
                            business_name=business_name,
                            name=business_name
                        )
                    else:
                        created = False
                    
                    user.mobile_number = mobile_number
                    user.email         = email
                    user.name          = business_name
                    user.business_name = business_name
                    user.save()

                except IntegrityError as e:
                    skipped_business_names.append(business_name)
                    return {'msg': f'User not created due to duplicate key error: {str(e)}'}
                except Exception as e:
                    return {'msg': f'Error creating/updating user: {str(e)}'}

                if created:
                    business_page = Business.objects.create(owner=user, business_name=business_name)
                else:
                    try:
                        business_page = Business.objects.get(owner=user)
                    except Exception as e:
                        pass
                        # return {'msg': f'Not able to Found the Business page {str(e)}'}

                #Category
                category, create = Category.objects.get_or_create(type=category_type)
                
                #Subcategory
                try:
                    sub_category       = str(row.get('Sub Category', ''))
                    if sub_category:
                        sub_category_names = [name.strip() for name in sub_category.split(',')]
                        subcategories      = [
                            SubCategory.objects.get_or_create(category=category, name=name)[0]
                                                for name in sub_category_names]
                    else:
                        subcategories = []
                except Exception as e:
                    subcategories = []
                    # return HttpJsonResponse(f"Error While Saving Sub Vategory Please check the data format: {str(e)}")
                
                #Product and Service
                try:
                    productservice = str(row.get('Product & Service', ''))
                    if productservice:
                        productservice_names = [name.strip() for name in productservice.split(',')]
                        productservices      = [
                            ProductService.objects.get_or_create(business=Business.objects.get(owner=user),name=name)[0]
                            for name in productservice_names
                        ]
                    else:
                        productservices = []
                except Exception as e:
                    productservices = []
                        # return HttpJsonResponse(f"Error while Saving the Product and Service Please check the data format: {str(e)}")
 
                #Extra Mobile Numbers
                try:
                    extra_mobile         = str(row.get('Extra Mobile No\'s', ''))
                    if extra_mobile:
                        extra_mobile_numbers = [names.strip() for names in extra_mobile.split(',')]
                        try:
                            business             = Business.objects.get(business_name=business_name)
                            extra_mobiles        = [BusinessMobileNumbers.objects.get_or_create(business=Business.objects.get(owner=business),
                                                                                                mobile_number=mobile_no)[0]
                                                                                                for mobile_no in extra_mobile_numbers]
                        except:
                            extra_mobiles = []
                    else:
                        extra_mobiles = []

                except Exception as e:
                    extra_mobiles = []
                        

                #Extra Mail IDs
                try:
                    extra_emailIDs = []
                    for email in email_ids[1:]:
                        existing_email = BusinessEmailID.objects.filter(business__owner=user, email=email).first()

                        if not existing_email:
                            new_email_id = BusinessEmailID.objects.create(
                                business=Business.objects.get(owner=user),
                                email=email
                            )
                            extra_emailIDs.append(new_email_id)
                except:
                    extra_emailIDs = []
                    
                #Brands
                try:
                    brand  = str(row.get('Brand', ''))
                    if brand:
                        brands = [name.strip() for name in brand.split(',')]
                        all_brands = [
                            BrandBusinessPage.objects.get_or_create(brand_name=brand_names)[0]
                                        for brand_names in brands
                                        ]

                        for brand_obj in all_brands:
                            brand_obj.category.add(category)
                    else:
                        all_brands = []

                except:
                    all_brands = []

                try:
                    try:
                        existing_business_mobile_number   = Business.objects.get(mobile_number=mobile_number)
                        existing_business_whatsapp_number = Business.objects.get(whatsapp_number=whatsapp_number)
                        existing_business_email           = Business.objects.get(email=first_email_id)
                
                        if existing_business_mobile_number:
                            existing_business_mobile_number.mobile_number = mobile_number
                        else:
                            business_page.mobile_number      = mobile_number

                        if existing_business_whatsapp_number:
                            existing_business_whatsapp_number.whatsapp_number = whatsapp_number
                        else:
                            business_page.whatsapp_number = whatsapp_number

                        if existing_business_email:
                            existing_business_email.email = first_email_id
                        else:
                            business_page.email = first_email_id

                        business_page.business_name = business_name
                        business_page.category           = category
                        business_page.state              = state
                        business_page.city               = city
                        business_page.pincode            = pincode
                        business_page.address            = Address
                        business_page.website_url        = Website

                        if GSTIN:
                            business_page.GSTIN          = GSTIN

                        if CIN_No:
                            business_page.CIN_No         = CIN_No

                        if DIN:
                            business_page.DIN            = DIN

                        if Company_No:
                            business_page.company_No     = Company_No
                            
                        business_page.RoC                  = RoC
                        business_page.director             = Director
                        business_page.business_info        = About_my_Business
                        business_page.services             = Product_Service
                        business_page.keywords             = Search
                        business_page.established_on       = established_on
                        business_page.subcategory.set(subcategories)
                        business_page.brand.set(all_brands)
                        business_page.save()
                    except Exception as e:
                        business_page.business_name      = business_name
                        business_page.mobile_number      = mobile_number
                        business_page.whatsapp_number    = whatsapp_number
                        business_page.email              = first_email_id    
                        business_page.email              = first_email_id
                        business_page.category           = category
                        business_page.state              = state
                        business_page.city               = city
                        business_page.pincode            = pincode
                        business_page.address            = Address
                        business_page.website_url        = Website

                        if GSTIN:
                            business_page.GSTIN          = GSTIN

                        if CIN_No:
                            business_page.CIN_No         = CIN_No

                        if DIN:
                            business_page.DIN            = DIN

                        if Company_No:
                            business_page.company_No     = Company_No
                            
                        business_page.RoC                  = RoC
                        business_page.director             = Director
                        business_page.business_info        = About_my_Business
                        business_page.services             = Product_Service
                        business_page.keywords             = Search
                        business_page.established_on       = established_on
                        business_page.subcategory.set(subcategories)
                        business_page.brand.set(all_brands)
                        business_page.save()

                    uid = urlsafe_base64_encode(force_bytes(business_page.id))

                        # token = generate_business_token(business_page)
                   
                except Exception as e:
                  #   return HttpJsonResponse(f"Problem While Saving the business Page: {str(e)}")    
                    # return {'msg': f"Problem While Saving the business Page: {str(e)}"}
                    pass
                

            except Exception as e:
                print(f'Error while saving data: {str(e)} {skipped_business_names}')
               #  return HttpJsonResponse(f'error while saving data {str(e)}')
                return {'msg': f'Error while savin data {str(e)}'}

            link = f'https://famousbusiness.in/userprofile/{business_page.business_name}?z_id={business_page.pk}'
            # print(link)

            body = 'Your Business page has been created please cklick on the link' + ' ' + link + ' '
            data = {
                'subject': 'Elevate Your Business with Exclusive PAN India Leads',
                'body': body,
                'to_email': user.email
            }
            # send_email.delay(data)

        if skipped_numbers:
            # return HttpJsonResponse(f'Mobile numbers with more than 15 digits: {", ".join(map(str, skipped_numbers))}')
            return {'msg': 'uploaded Successfully'}

      #   JsonResponse_data = {'msg': 'Mail has been sent to the user'}



# class Utils: 
#     @staticmethod
#     def send_mail(data):
#         email = EmailMessage(
#             subject=data['subject'],
#             body= data['body'],
#             html_content = render_to_string('../templates/mail/send_mail.html', {'business_id': business_id}),
#             from_email = 'customercare@famousbusiness.in',
#             to=[data['to_email']]
#         )

#         email.send()
        



# Send whatsapp message while upload Business excel file
@shared_task(task_rate_limit='6/m')
def send_whatsapp_msg_while_registration(data):
        # for business_data in data:
        #     mobile_number = business_data.get('mobile_number') 
        #     business_name = business_data.get('business_name')
        #     category      = business_data.get('business_category')
        #     email         = business_data.get('to_email')
            # api_url = "https://bhashsms.com/api/sendmsg.php"
            api_url = "https://trans.smsfresh.co/api/sendmsg.php"
            mobile_number = data["mobile_number"]
            business_name = data["business_name"]
            category      = data["business_category"]
            email         = data["to_email"]

            params = {
                "user" : "WEBZOTICA",
                "pass" : "123456",
                "sender" : "BUZWAP",
                "phone" : mobile_number,
                "text": "status_change",
                "priority" : "wa",
                "stype" : "normal",
                "Params": f"{business_name}, {category}",
                "htype" : "image",
                "imageUrl" : "https://mdwebzotica.famousbusiness.in/business_register.jpg"
            }

            print('time',time.time())
            
            url = f"{api_url}?user={params['user']}&pass={params['pass']}&sender={params['sender']}&phone={params['phone']}&text={params['text']}&priority={params['priority']}&stype={params['stype']}&htype={params['htype']}&url={params['imageUrl']}"

            response = requests.get(url, params=params)

            response_data = {
                "status-code": response.status_code
            }

            return response_data



