from rest_framework import serializers
from django.contrib.auth.models import User

from user.models import Profile

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', '')
        )
        return user

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