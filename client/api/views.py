from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User

from .serializers import ClientSerializer
from client.models import Client


class ClientsView(APIView):

    def get(self, request, queryset=None, **kwargs):
        provider = self.kwargs.get('pk')
        if User.objects.filter(username=provider).exists():
            provider_user = User.objects.get(username=provider)
            clients = Client.objects.filter(provider=provider_user)
            data = []
            for client in clients:
                data.append(ClientSerializer(client).data)
            return Response(status=status.HTTP_200_OK, data=data)
        else:
            data = {'message': 'Provider does not exist.'}
            return Response(status=status.HTTP_404_NOT_FOUND, data=data)
    
class ClientView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, queryset=None, **kwargs):
        client_id = self.kwargs.get('pk') 
        client = Client.objects.get(id=client_id)
        data = ClientSerializer(client).data
        return Response(status=status.HTTP_200_OK, data=data)

    def post(self, request, queryset=None, **kwargs):
        provider = self.kwargs.get('pk')
        data = request.data
        action = data['action']
        response = {'OK': False}
        if action == 'delete':
            if Client.objects.filter(id=provider).exists():
                client = Client.objects.get(id=provider)
                client.delete()
                response['message'] = "Client Deleted."
                response['OK'] = True
                return Response(status=status.HTTP_200_OK, data=response)
            else:
                response['message'] = "Client not found."
                return Response(status=status.HTTP_200_OK, data=response)
        client_provider = User.objects.get(username=provider)
        if action == 'new':
            name = data['name']
            last_name = data.get('last_name', 'no last name saved')
            phone = data.get('phone', 'no phone saved')
            email = data.get('email', 'no email saved')
            address = data.get('address', 'no address saved')
            new_client = Client(provider=client_provider, name=name, last_name=last_name, phone=phone, email=email, address=address)
            new_client.image = data.get('image', new_client.image)
            new_client.save()
            response['message'] = "New client created."
            response['OK'] = True
        if action == 'update':
            if not data.get('id'):
                response['message'] = "Client id required."
                return Response(status=status.HTTP_200_OK, data=response)
            if Client.objects.filter(id=data['id']).exists():
                client = Client.objects.get(id=data['id'])
                client.name = data.get('name', client.name)
                client.last_name = data.get('last_name', client.last_name)
                client.email = data.get('email', client.email)
                client.phone = data.get('phone', client.phone)
                client.address = data.get('address', client.address)
                client.image = data.get('image', client.image)
                client.save()
                response['message'] = "Client Updated."
                response['OK'] = True
                return Response(status=status.HTTP_200_OK, data=response)
            else:
                response['message'] = "Client not found."
                return Response(status=status.HTTP_200_OK, data=response)
        return Response(status=status.HTTP_200_OK, data=response)  
