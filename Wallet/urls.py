from django.urls import path
from .views import UserWalletBalanceView, UserMatureImmatureWallet, UpdateWalletBalanceView, AllUserTransactionsView, UserBankAccountView, UserWithdrawalAPIView, TransferMoneyView





urlpatterns = [
    path('account/balance', UserWalletBalanceView.as_view(), name='user_wallet_data'),
    path('mature/immature/balance', UserMatureImmatureWallet.as_view(), name='user_mature_immature_wallet_data'),
    path('update/wallet/balance', UpdateWalletBalanceView.as_view(), name='update_wallet_balance'),
    path('all/wallet/transactions/', AllUserTransactionsView.as_view(), name='all_user_transactions'),
    path('user/bank/', UserBankAccountView.as_view(), name='user_bank_accounts'),
    path('user/withdrawal/requests/', UserWithdrawalAPIView.as_view(), name='user_withdrawl_request'),
    path('transfer/money/', TransferMoneyView.as_view(), name='transfer_money'),
]

