from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User

from .serializers import BusinessSerializer
from business.models import Business

class BusinessesView(APIView):

    def get(self, request, queryset=None, **kwargs):
        owner = self.kwargs.get('pk')
        print(owner)
        if User.objects.filter(username=owner).exists():
            owner_user = User.objects.get(username=owner)
            businesses = Business.objects.filter(owners=owner_user)
            data = []
            for business in businesses:
                data.append(BusinessSerializer(business).data)
            return Response(status=status.HTTP_200_OK, data=data)
        else:
            data = {'message': 'Owner does not exist.'}
            return Response(status=status.HTTP_404_NOT_FOUND, data=data)
    
class BusinessView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, queryset=None, **kwargs):
        owner_id = self.kwargs.get('pk') 
        business = Business.objects.get(id=owner_id)
        data = BusinessSerializer(business).data
        return Response(status=status.HTTP_200_OK, data=data)

    def post(self, request, queryset=None, **kwargs):
        pk = self.kwargs.get('pk')
        data = request.data
        action = data['action']
        response = {'OK': False}
        if action == 'delete':
            if Business.objects.filter(id=pk).exists():
                business = Business.objects.get(id=pk)
                business.delete()
                response['message'] = "Business Deleted."
                response['OK'] = True
                return Response(status=status.HTTP_200_OK, data=response)
            else:
                response['message'] = "Business not found."
                return Response(status=status.HTTP_200_OK, data=response)
        owner = User.objects.get(username=pk)
        if action == 'new':
            name = data['name']
            description = data.get('description', 'no description saved')
            phone = data.get('phone', 'no phone saved')
            email = data.get('email', 'no email saved')
            address = data.get('address', 'no address saved')
            new_business = Business(name=name, description=description, phone=phone, email=email, address=address)
            new_business.logo = data.get('image', new_business.logo)
            new_business.save()
            new_business.owners.set([owner])
            response['message'] = "New business created."
            response['OK'] = True
        if action == 'update':
            if not data.get('id'):
                response['message'] = "Business id required."
                return Response(status=status.HTTP_200_OK, data=response)
            if Business.objects.filter(id=data['id']).exists():
                business = Business.objects.get(id=data['id'])
                business.name = data.get('name', business.name)
                business.description = data.get('description', business.description)
                business.email = data.get('email', business.email)
                business.phone = data.get('phone', business.phone)
                business.address = data.get('address', business.address)
                business.logo = data.get('image', business.logo)
                business.save()
                business_data = BusinessSerializer(business).data
                response['message'] = "Business Updated."
                response['business'] = business_data
                response['OK'] = True
                return Response(status=status.HTTP_200_OK, data=response)
            else:
                response['message'] = "Business not found."
                return Response(status=status.HTTP_200_OK, data=response)
        return Response(status=status.HTTP_200_OK, data=response)  
