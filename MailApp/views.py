from Listings.models import Business
from .task import send_test_email
from django.http import HttpResponse
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.shortcuts import render
from Listings.models import Category
from .cities import CITIES





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