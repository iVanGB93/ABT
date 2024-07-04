from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User


from .serializers import ItemSerializer, ItemListSerializer
from job.api.serializers import JobSerializer
from item.models import Item, Item_List

class ItemsView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, queryset=None, **kwargs):
        provider = self.kwargs.get('pk')
        provider_user = User.objects.get(username=provider)
        item_list = Item_List.objects.filter(provider=provider_user)
        print(item_list)
        data = []
        for item in item_list:
            data.append(ItemListSerializer(item).data)
        return Response(status=status.HTTP_200_OK, data=data)
    
    def post(self, request, queryset=None, **kwargs):
        response = {'OK': False}
        provider = self.kwargs.get('pk')
        data = request.data
        action = data['action']
        if action == 'delete':
            if Item_List.objects.filter(id=provider).exists():
                item_list = Item_List.objects.get(id=provider)
                item_list.delete()
                response['message'] = "Item Deleted."
                response['OK'] = True
                return Response(status=status.HTTP_200_OK, data=response)
            else:
                response['message'] = "Item not found."
                return Response(status=status.HTTP_200_OK, data=response)
        provider_user = User.objects.get(username=provider)
        if action == 'new':
            new_item_list = Item_List(provider=provider_user, name=data['name'], amount=data['amount'], price=data['price'])
            new_item_list.description = data.get('description', 'no description added')
            new_item_list.image = data.get('image', new_item_list.image)
            new_item_list.save()
            response['message'] = "New Item created."
            response['OK'] = True
        if action == 'update':
            if Item_List.objects.filter(id=pk).exists():
                item_list = Item_List.objects.get(id=pk)
                item_list.name = data.get('name', item_list.name)
                item_list.description = data.get('description', item_list.description)
                item_list.amount = data.get('amount', item_list.amount)
                item_list.price = data.get('price', item_list.price)
                item_list.image = data.get('image', item_list.image)
                item_list.save()
                response['message'] = "Item Updated."
                response['OK'] = True
                return Response(status=status.HTTP_200_OK, data=response)
            else:
                response['message'] = "Item not found."
                return Response(status=status.HTTP_200_OK, data=response)
        return Response(status=status.HTTP_200_OK, data=response)
    

class ItemView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, queryset=None, **kwargs):
        pk = self.kwargs.get('pk')
        if pk == 'all':
            item_list = Item_List.objects.all()
            data = []
            for item in item_list:
                data.append(ItemListSerializer(item).data)
        else:
            item_list = Item_List.objects.get(id=pk)
            used_items = item_list.item_set.all()
            data = []
            for item in used_items:
                job = item.job
                data.append(JobSerializer(job).data)
        return Response(status=status.HTTP_200_OK, data=data)
    
    def post(self, request, queryset=None, **kwargs):
        pk = self.kwargs.get('pk')
        data = request.data
        print("ITEM DATA", data)
        action = data['action']
        response = {'OK': False}
        if action == 'new':
            new_item_list = Item_List(name=data['name'], amount=data['amount'], price=data['price'])
            new_item_list.description = data.get('description', 'no description added')
            new_item_list.image = data.get('image', new_item_list.image)
            new_item_list.save()
            response['message'] = "New Item created."
            response['OK'] = True
        if action == 'update':
            if Item_List.objects.filter(id=pk).exists():
                item_list = Item_List.objects.get(id=pk)
                item_list.name = data.get('name', item_list.name)
                item_list.description = data.get('description', item_list.description)
                item_list.amount = data.get('amount', item_list.amount)
                item_list.price = data.get('price', item_list.price)
                item_list.image = data.get('image', item_list.image)
                item_list.save()
                response['message'] = "Item Updated."
                response['OK'] = True
                return Response(status=status.HTTP_200_OK, data=response)
            else:
                response['message'] = "Item not found."
                return Response(status=status.HTTP_200_OK, data=response)
        if action == 'delete':
            if Item_List.objects.filter(id=pk).exists():
                item_list = Item_List.objects.get(id=pk)
                item_list.delete()
                response['message'] = "Item Deleted."
                response['OK'] = True
                return Response(status=status.HTTP_200_OK, data=response)
            else:
                response['message'] = "Item not found."
                return Response(status=status.HTTP_200_OK, data=response)
        return Response(status=status.HTTP_200_OK, data=response)
    

class SpentsView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, queryset=None, **kwargs):
        pk = self.kwargs.get('pk')
        item_list = Item_List.objects.get(id=pk)
        used_items = item_list.item_set.all()
        data = []
        for item in used_items:
            job = item.job
            data.append(JobSerializer(job).data)
        return Response(status=status.HTTP_200_OK, data=data)