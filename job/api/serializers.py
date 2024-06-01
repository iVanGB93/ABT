from rest_framework import serializers
from job.models import Job, Spent, Invoice, Charge
from user.models import Profile
from item.models import Item_List, Item


class JobSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ('id', 'status', 'client', 'description', 'address', 'price', 'date', 'image')
    
    def get_client(self, obj):
        return obj.client.user.username

class ClientSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('id', 'user', 'phone', 'address', 'email', 'image')
    
    def get_user(self, obj):
        return obj.user.username

    def get_email(self, obj):
        return obj.user.email

class ItemListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item_List
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item
        fields = '__all__'

class SpentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Spent
        fields = '__all__'

class InvoiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Invoice
        fields = '__all__'
    
class ChargeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Charge
        fields = '__all__'