from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User


from .serializers import ItemSerializer, ItemListSerializer
from item.models import Item, Item_List

class ItemsView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, queryset=None, **kwargs):
        provider = self.kwargs.get('pk')
        provider_user = User.objects.get(username=provider)
        item_list = Item_List.objects.filter(provider=provider_user)
        data = []
        for item in item_list:
            data.append(ItemListSerializer(item).data)
        return Response(status=status.HTTP_200_OK, data=data)