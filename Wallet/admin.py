from django.contrib import admin
from .models import Transaction, ImmatureWallet, MatureWallet, Withdrawals, UserBankAccount



admin.site.register(Withdrawals)
admin.site.register(ImmatureWallet)
admin.site.register(MatureWallet)
admin.site.register(Transaction)
admin.site.register(UserBankAccount)

