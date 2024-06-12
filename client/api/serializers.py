from rest_framework import serializers

from client.models import Client


class ClientSerializer(serializers.ModelSerializer):
    provider = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = ('id', 'provider', 'name', 'last_name', 'phone', 'address', 'email', 'image')
    
    def get_provider(self, obj):
        return obj.provider.username