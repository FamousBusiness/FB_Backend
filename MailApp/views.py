from Listings.models import Business
from .task import send_test_email
from django.http import HttpResponse
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.shortcuts import render
from Listings.models import Category
from .cities import CITIES
from PremiumPlan.models import PremiumPlanOrder
from uuid import uuid4





def SendTestMail(request):
    business = Business.objects.all()[1]
    # business = Business.objects.all()[141]

    business_name = business.business_name
    
    data = {
        'business_name': business.business_name,
        'email': 'sahooranjitkumar53@gmail.com',
        'requirements': "CCTV Requirements",
        'customer_name': "Testing Customer",
        "location": "Delhi"
       
    }

    send_test_email.delay(data)

    return HttpResponse('Done')




def ManuallMailView(request):
    categories = Category.objects.all()
    cities = CITIES

    if request.method == 'POST':
        from_mail = request.POST.get("from_email")
        category  = request.POST.get('category')  
        city  = request.POST.get('city')  
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        try:
            cat = Category.objects.get(type=category)
        except Exception as e:
            return HttpResponse(f"Unable to find the category: {str(e)}")
        
        try:
            business_pages = Business.objects.filter(city=city, category=cat)
        except Exception as e:
            return HttpResponse(f"Unable to find the business page: {str(e)}")
        
        if business_pages:
            business_email = [business.email for business in business_pages]
            
            data = {
                'from_email': from_mail,
                'subject': subject,
                'message': message
            }
        
    return render(request, 'mail/manual_mail.html', {'category': categories, 'cities': cities})



def SendMailToBusinessOwnerWiseView(request):
    # business = Business.objects.filter(id__gte=1, id__lte=2)
    # business = Business.objects.all()[11001:12000]
    business  = Business.objects.all()[251:300]
    # for business_page in business:
    #     print(business_page.pk)

    data = [{
        'email': business_page.email,
        'business_id': business_page.pk,
        'name': business_page.business_name,
        'uid': urlsafe_base64_encode(force_bytes(business_page.business_name)),
        # 'token': PasswordResetTokenGenerator().make_token(business_page.business_name)
    } for business_page in business]

    # send_email.delay(data)

    return HttpResponse('Done')




from django.http import HttpResponse
import pdfkit
from django.core.files.base import ContentFile


def generate_pdf_from_html(request):
    request_user = request.user

    premium_plan_order = PremiumPlanOrder.objects.get(user = request_user)
    business           = Business.objects.get(owner = request_user)

    plan_amount = int(premium_plan_order.amount)
    gst         = (plan_amount / 100) * 18

    premium_plan = premium_plan_order.premium_plan
    lead_view_quantity = premium_plan.lead_view if premium_plan else 0

    random_invoice_no = str(uuid4())[:25]

    html_content = f"""
            <!DOCTYPE html>
            <html>
                <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            margin: 20px;
                        }}
                        .header {{
                            text-align: center;
                            font-size: 24px;
                            font-weight: bold;
                        }}
                        .sub-header {{
                            text-align: center;
                            font-size: 18px;
                        }}
                        .from-to {{
                            display: flex;
                            justify-content: space-between;
                            margin: 20px 0;
                        }}
                        .from, .to {{
                            width: 45%;
                        }}
                        .from h3, .to h3 {{
                            margin-bottom: 5px;
                        }}
                        table {{
                            width: 100%;
                            border-collapse: collapse;
                            margin-top: 20px;
                        }}
                        th, td {{
                            border: 1px solid #000;
                            padding: 10px;
                            text-align: left;
                        }}
                        .total {{
                            text-align: right;
                            margin-top: 20px;
                        }}
                        .note {{
                            margin-top: 30px;
                            font-size: 12px;
                        }}
                    </style>
                </head>

                <body>
                    <div class="header">TAX INVOICE</div>

                    <div class="sub-header">Famous Business</div>

                    <div class="from-to">
                        <div class="from">
                            <h3>FROM:</h3>
                            <p>WEBZOTICA BUSINESS FAMOUS SOFTWARE PRIVATE LIMITED<br>
                            Faridabad, Haryana, India<br>
                            GSTIN: 06AADCW6644C1ZF</p>
                        </div>

                        <div class="to">
                            <h3>Billing To:</h3>
                            <p>{business.business_name}<br/>
                                {business.city}, {business.state}, India<br>
                            </p>
                        </div>
                    </div>

                    <div>Date: 28/12/2024<br>INVOICE No: {random_invoice_no}</div>

                    <table>
                        <tr>
                            <th>Item Description</th>
                            <th>Qty</th>
                            <th>HSN Code</th>
                            <th>Unit Price</th>
                            <th>Total Price</th>
                        </tr>
                        <tr>
                            <td>Business Plan Subscription</td>
                            <td>{premium_plan_order.premium_plan}</td>
                            <td>998361</td>
                            <td>Rs.{plan_amount - gst}</td>
                            <td>Rs.{plan_amount - gst}</td>
                        </tr>
                    </table>

                    <p>(The Business Plan offers {lead_view_quantity} leads/month)</p>

                    <div class="total">
                        SUB TOTAL: Rs.{plan_amount - gst}<br>
                        TAX (18%): Rs.{gst}<br>
                        GRAND TOTAL: Rs.{plan_amount}
                    </div>

                    <div class="note">
                        <p>Note: This invoice is auto-generated and does not require a signature. For any queries, please contact<br>
                        customercare@famousbusiness.in  Helpline: 080-62181258</p>
                    </div>
                </body>
            </html>
        """
    
    pdf_bytes = pdfkit.from_string(html_content, False)

    premium_plan_order.invoice.save(
            f'invoice{premium_plan_order.pk}.pdf',
            ContentFile(pdf_bytes)
        )
    premium_plan_order.save()

    print(premium_plan_order.invoice)

    return HttpResponse()

    # # Return the PDF file in response
    # response = HttpResponse(pdf, content_type='application/pdf')
    # response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'

    # return response






