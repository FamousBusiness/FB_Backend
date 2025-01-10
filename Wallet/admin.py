from django.contrib import admin
from .models import Wallet, Transaction, ImmatureWallet, MatureWallet



admin.site.register(Wallet)
admin.site.register(ImmatureWallet)
admin.site.register(MatureWallet)
admin.site.register(Transaction)

