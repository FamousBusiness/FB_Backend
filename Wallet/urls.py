from django.urls import path
from .views import UserWalletBalanceView, UserMatureImmatureWallet





urlpatterns = [
    path('account/balance', UserWalletBalanceView.as_view(), name='user_wallet_data'),
    path('mature/immature/balance', UserMatureImmatureWallet.as_view(), name='user_mature_immature_wallet_data'),
]

