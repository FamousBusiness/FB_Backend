from django.contrib import admin
from .models import Transaction, ImmatureWallet, MatureWallet, Withdrawals, UserBankAccount, AddMoneyFee, TransferMoneyFee, PhonpeWalletOrder, CODFee, PrepaidFee



admin.site.register(Withdrawals)
admin.site.register(ImmatureWallet)
admin.site.register(MatureWallet)
admin.site.register(Transaction)
admin.site.register(UserBankAccount)
admin.site.register(AddMoneyFee)
admin.site.register(TransferMoneyFee)
admin.site.register(PhonpeWalletOrder)
admin.site.register(CODFee)
admin.site.register(PrepaidFee)

