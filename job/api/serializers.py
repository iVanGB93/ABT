from rest_framework import serializers
from job.models import Job
from user.models import Profile


class JobSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ('id', 'client', 'description', 'address', 'price')
    
    def get_client(self, obj):
        return obj.client.user.username

class ClientSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('id', 'user', 'phone', 'address')
    
    def get_user(self, obj):
        return obj.user.username