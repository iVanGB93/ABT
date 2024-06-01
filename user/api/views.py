from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import ClientSerializer
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
        profile = Profile.objects.get(user=new_user)
        profile.is_client = False
        profile.save()
        response['message'] = "Account created."
        return Response(status=status.HTTP_201_CREATED, data=response)

class ClientsView(APIView):

    def get(self, request, queryset=None, **kwargs):
        provider = self.kwargs.get('pk')
        provider_user = User.objects.get(username=provider)
        clients = Profile.objects.filter(is_client=True, provider=provider_user)
        data = []
        for client in clients:
            data.append(ClientSerializer(client).data)
        return Response(status=status.HTTP_200_OK, data=data)
    
class ClientView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, queryset=None, **kwargs):
        client_id = self.kwargs.get('pk') 
        client = Profile.objects.get(id=client_id)
        data = ClientSerializer(client).data
        return Response(status=status.HTTP_200_OK, data=data)

    def post(self, request, queryset=None, **kwargs):
        provider = self.kwargs.get('pk')
        provider_user = User.objects.get(username=provider)
        data = request.data
        action = data['action']
        response = {'OK': False}
        if action == 'new':
            username = data['name']
            email = data['email']
            if User.objects.filter(username=username).exists():
                response['message'] = "Name is already taken."
                return Response(status=status.HTTP_200_OK, data=response)
            new_user = User(username=username, email=email)
            new_user.first_name = username
            new_user.set_password('temporaryPassword')
            new_user.save()
            profile = Profile.objects.get(user=new_user)
            profile.phone = data.get('phone', profile.phone)
            profile.address = data.get('address', profile.address)
            profile.image = data.get('image', profile.image)
            profile.provider = provider_user
            profile.save()
            response['message'] = "New client created."
            response['OK'] = True
        if action == 'update':
            if not data.get('id'):
                response['message'] = "Client id required."
                return Response(status=status.HTTP_200_OK, data=response)
            if Profile.objects.filter(id=data['id']).exists():
                profile = Profile.objects.get(id=data['id'])
                profile.phone = data.get('phone', profile.phone)
                profile.address = data.get('address', profile.address)
                profile.image = data.get('image', profile.image)
                profile.save()
                user = profile.user
                user.username = data['name']
                user.first_name = data['name']
                user.email = data.get('email', user.email)
                user.save()
                response['message'] = "Client Updated."
                response['OK'] = True
                return Response(status=status.HTTP_200_OK, data=response)
            else:
                response['message'] = "Client not found."
                return Response(status=status.HTTP_200_OK, data=response)
        if action == 'delete':
            if Profile.objects.filter(id=data['id']).exists():
                profile = Profile.objects.get(id=data['id'])
                user = profile.user
                user.delete()
                response['message'] = "Client Deleted."
                response['OK'] = True
                return Response(status=status.HTTP_200_OK, data=response)
            else:
                response['message'] = "Client not found."
                return Response(status=status.HTTP_200_OK, data=response)
        return Response(status=status.HTTP_200_OK, data=response)  
