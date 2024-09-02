from django.urls import path
from .transaction_views import GetAllTransactionView, UserWalletAPIView

urlpatterns = [
    path('', GetAllTransactionView.as_view(), name='get_all_transactions_details'),
      path('users-wallet/',UserWalletAPIView.as_view(), name='users_wallet'),
]
