from rest_framework import serializers

from client.models import Client


class ClientSerializer(serializers.ModelSerializer):
    provider = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = (
            'id', 
            'business', 
            'provider', 
            'name', 
            'last_name', 
            'phone', 
            'address', 
            'email', 
            'image', 
            'created_at', 
            'updated_at'
        )

    def get_provider(self, obj):
        return obj.provider.username