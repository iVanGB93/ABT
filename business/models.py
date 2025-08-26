from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
import os

def upload_to_business(instance, filename):
    filename = os.path.basename(filename)
    return f'business/{instance.name}/{filename}'

class Business(models.Model):
    owners = models.ManyToManyField(User, related_name='businesses')
    name = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=255)
    address2 = models.CharField(max_length=50, default='no extra address saved')
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    logo = models.ImageField(upload_to=upload_to_business, default='logoDefault.jpg')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Business'
        verbose_name_plural = 'Businesses'
        ordering = ['name']

def upload_to_extra_income(instance, filename):
    filename = os.path.basename(filename)
    return f'extra_income/{instance.business.name}/{filename}'

class PaymentMethodType(models.Model):
    code = models.CharField(max_length=20, unique=True)  # 'paypal', 'cashapp', etc.
    name = models.CharField(max_length=50)  # 'PayPal', 'CashApp', etc.
    icon = models.CharField(max_length=50, blank=True)  # Nombre del ícono
    requires_email = models.BooleanField(default=False)
    requires_phone = models.BooleanField(default=False)
    requires_username = models.BooleanField(default=False)
    supports_deep_links = models.BooleanField(default=False)
    deep_link_pattern = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
class BusinessPaymentMethod(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='payment_methods')
    payment_type = models.ForeignKey(PaymentMethodType, on_delete=models.CASCADE)
    
    # Campos genéricos para diferentes tipos
    account_email = models.EmailField(blank=True, null=True)
    account_phone = models.CharField(max_length=20, blank=True, null=True)
    account_username = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=100, blank=True, null=True)
    
    # Configuración
    is_enabled = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    display_name = models.CharField(max_length=100, blank=True)  # Personalizable
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['business', 'payment_type']
    
    def __str__(self):
        return f"{self.business.name} - {self.payment_type.name}"
    
    def get_payment_link(self, amount=None):
        """Genera link de pago si es soportado"""
        if not self.payment_type.supports_deep_links:
            return None
            
        pattern = self.payment_type.deep_link_pattern
        if pattern:
            return pattern.format(
                username=self.account_username,
                email=self.account_email,
                amount=amount or ''
            )
        return None

class ExtraIncome(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='extra_income')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to=upload_to_extra_income, default='incomeDefault.jpg')

    def __str__(self):
        return f"{self.description} - {self.amount}"

    class Meta:
        verbose_name = 'Extra Income'
        verbose_name_plural = 'Extra Incomes'
        ordering = ['-date']

def upload_to_extra_expense(instance, filename):
    filename = os.path.basename(filename)
    return f'extra_expense/{instance.business.name}/{filename}'

class ExtraExpense(models.Model):
    CATEGORY_CHOICES = [
        ('office_supplies', 'Office Supplies'),
        ('utilities', 'Utilities'),
        ('marketing', 'Marketing'),
        ('other', 'Other'),
        ('travel', 'Travel'),
        ('maintenance', 'Maintenance'),
        ('salaries', 'Salaries'),
        ('taxes', 'Taxes'),
        ('medical_insurance', 'Medical Insurance'),
        ('insurance', 'Insurance'),
        ('equipment', 'Equipment'),
        ('software', 'Software'),
        ('legal_fees', 'Legal Fees'),
        ('training', 'Training'),
        ('research', 'Research'),
        ('licenses', 'Licenses'),
        ('repairs', 'Repairs'),
        ('shipping', 'Shipping'),
        ('warranty', 'Warranty'),
        ('fines', 'Fines'),
        ('commissions', 'Commissions'),
        ('bank_fees', 'Bank Fees'),
        ('interest', 'Interest'),
        ('fuel', 'Fuel'),
        ('meals', 'Meals'),
        ('personal_account', 'Personal Account')
    ]
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='extra_expenses')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to=upload_to_extra_expense, default='expenseDefault.jpg')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    tax_deductible = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.description} - {self.amount}"

    class Meta:
        verbose_name = 'Extra Expense'
        verbose_name_plural = 'Extra Expenses'
        ordering = ['-date']

def invitationCode():    
    while True:
        code = get_random_string(length=8, allowed_chars="1234567890")
        if Invitation.objects.filter(code=code).count() == 0:
            break
    return code

class Invitation(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='invitations')
    inviter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    email = models.EmailField(max_length=254)
    code = models.CharField(max_length=50, default=invitationCode, unique=True)
    date_sent = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"Invitation to {self.email} for {self.business.name}"

