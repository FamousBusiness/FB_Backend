from django.urls import path
from .transaction_views import GetAllTransactionView

urlpatterns = [
    path('', GetAllTransactionView.as_view(), name='get_all_transactions_details'),
]
