from rest_framework import serializers

from business.models import Business, ExtraIncome, ExtraExpense, PaymentMethodType, BusinessPaymentMethod


class BusinessSerializer(serializers.ModelSerializer):
    owners = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Business
        fields = ('id', 'owners', 'name', 'phone', 'address', 'address2', 'email', 'logo', 'website', 'description', 'created_at', 'updated_at')

class ExtraIncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtraIncome
        fields = '__all__'

class ExtraExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtraExpense
        fields = '__all__'

class PaymentMethodTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethodType
        fields = '__all__'

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessPaymentMethod
        fields = '__all__'