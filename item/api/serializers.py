from rest_framework import serializers

from item.models import Item, Item_List


class ItemListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item_List
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item
        fields = '__all__'