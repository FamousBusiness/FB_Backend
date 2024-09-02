from Listings.models import Order
from PremiumPlan.models import PremiumPlan
import razorpay
from IFBD_Project.settings import (
    RAZORPAY_KEY_ID,
    RAZORPAY_KEY_SECRET,
)
import json
from .constants import PaymentStatus



def ADSPaymentfunc(data):
    user = data['user']
    amount = data['amount']
    plan = data['plan_id']

    try:
        plan = PremiumPlan.objects.get(id=plan)
    except PremiumPlan.DoesNotExist:
        return {'error': 'Invalid Plan ID'}

    client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

    razorpay_order = client.order.create(
            {"amount": int(amount) * 100, "currency": "INR", "payment_capture": "1"}
        )
    order = Order.objects.create(
        user=user,plan=plan ,amount=amount, provider_order_id=razorpay_order["id"]
    )
    order.save()
    

    data = {
        "razorpay_order": razorpay_order,
        "order": order,
        "razorpay_key": RAZORPAY_KEY_ID
    }
            
    return data
    


def ADSPaymentCallbackView(request):
    def verify_signature(response):
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        return client.utility.verify_payment_signature(response)

    if "razorpay_signature" in request.POST:
        payment_id = request.POST.get("razorpay_payment_id", "")
        provider_order_id = request.POST.get("razorpay_order_id", "")
        signature_id = request.POST.get("razorpay_signature", "")
        order = Order.objects.get(provider_order_id=provider_order_id)
        order.payment_id = payment_id
        order.signature_id = signature_id

        order.save()

        if not verify_signature():
            order.status = PaymentStatus.SUCCESS
            order.save()
        else:
            order.status = PaymentStatus.FAILURE
            order.save()
            
    else:
        payment_id = json.loads(request.POST.get("error[metadata]")).get("payment_id")
        provider_order_id = json.loads(request.POST.get("error[metadata]")).get(
            "order_id"
        )
        order = Order.objects.get(provider_order_id=provider_order_id)
        order.payment_id = payment_id
        order.status = PaymentStatus.FAILURE
        order.save()



