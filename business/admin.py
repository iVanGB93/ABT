from django.contrib import admin
from .models import Business, ExtraIncome, ExtraExpense, Invitation, PaymentMethodType, BusinessPaymentMethod

admin.site.register(Business)
admin.site.register(ExtraIncome)
admin.site.register(ExtraExpense)
admin.site.register(Invitation)
admin.site.register(PaymentMethodType)
admin.site.register(BusinessPaymentMethod)
