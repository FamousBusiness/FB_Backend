from django.urls import path
from .views import (
    UserWalletBalanceView, UserMatureImmatureWallet, 
    UpdateWalletBalanceView, AllUserTransactionsView, 
    UserBankAccountView, UserWithdrawalAPIView, TransferMoneyView, ExportWithdrawalView,
    RecentTransactions, ExportTransactionsView, FilterUserTransactionsView, FilterWithDrawalView
)





urlpatterns = [
    path('account/balance', UserWalletBalanceView.as_view(), name='user_wallet_data'),
    path('stats/balance', UserMatureImmatureWallet.as_view(), name='user_mature_immature_wallet_data'),
    path('update/wallet/balance', UpdateWalletBalanceView.as_view(), name='update_wallet_balance'),
    path('all/wallet/transactions/', AllUserTransactionsView.as_view(), name='all_user_transactions'),
    path('user/bank/', UserBankAccountView.as_view(), name='user_bank_accounts'),
    path('user/withdrawal/requests/', UserWithdrawalAPIView.as_view(), name='user_withdrawl_request'),
    path('filter/withdrawal/', FilterWithDrawalView.as_view(), name='filter_withdrawal'),
    path('export/withdrawal/', ExportWithdrawalView.as_view(), name='export_withdrawal'),
    path('transfer/money/', TransferMoneyView.as_view(), name='transfer_money'),
    path('recent/transactions/', RecentTransactions.as_view(), name='recent_transaction'),
    path('export/transactions/', ExportTransactionsView.as_view(), name='export_transaction'),
    path('filter/transactions/', FilterUserTransactionsView.as_view(), name='filter_transaction')
]


