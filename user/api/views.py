from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import AccountSerializer
from rest_framework.parsers import MultiPartParser, FormParser

from user.models import Profile

class RegisterView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, queryset=None, **kwargs):
        data = request.data
        username = data['username']
        password = data['password']
        email = data['email']
        response = {'OK': False}
        if User.objects.filter(username=username).exists():
            response['message'] = "Username is already taken."
            return Response(status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION, data=response)
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        new_user.save()
        response['message'] = "Account created."
        return Response(status=status.HTTP_201_CREATED, data=response)

class AccountView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, queryset=None, **kwargs):
        user = self.kwargs.get('pk')
        user = User.objects.get(username=user)
        profile = Profile.objects.get(user=user)
        data = AccountSerializer(profile).data
        return Response(status=status.HTTP_200_OK, data=data)
    
    def post(self, request, queryset=None, **kwargs):
        data = request.data
        user = self.kwargs.get('pk')
        user = User.objects.get(username=user)
        profile = Profile.objects.get(user=user)
        profile.business_name = data.get('business_name', profile.business_name)
        profile.business_logo = data.get('business_logo', profile.business_logo)
        profile.phone = data.get('phone', profile.phone)
        profile.address = data.get('address', profile.address)
        profile.save()
        data = AccountSerializer(profile).data
        return Response(status=status.HTTP_200_OK, data=data)

