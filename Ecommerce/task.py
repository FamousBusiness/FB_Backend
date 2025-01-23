from celery import shared_task
from django.utils.timezone import now
from .models import ProductOrders
from Wallet.models import ImmatureWallet, MatureWallet




@shared_task
def transfer_funds_from_immature_to_mature():
    today = now().date()
    orders = ProductOrders.objects.filter(return_date__date=today, is_returned=False)

    for order in orders:
        immature_wallet = ImmatureWallet.objects.filter(user=order.user).first()
        mature_wallet   = MatureWallet.objects.filter(user=order.user).first()
        
        if immature_wallet and mature_wallet and order.payment_mode == 'Prepaid':
            cleaned_price = float(order.product.price.replace(',', ''))
            order_amount = cleaned_price * float(order.quantity)

            # Validation: Check if there is enough balance
            if immature_wallet.balance >= order_amount:
                # Deduct from ImmatureWallet
                immature_wallet.balance -= order_amount
                immature_wallet.save()

                # Add to MatureWallet
                mature_wallet.balance += order_amount
                mature_wallet.save()
                
                # Mark the order as processed
                order.is_returned = True
                order.returned_at = now()
                order.save()
