from rest_framework import serializers

from business.models import Business


class BusinessSerializer(serializers.ModelSerializer):
    owners = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Business
        fields = ('id', 'owners', 'name', 'phone', 'address', 'email', 'logo', 'website', 'description', 'created_at', 'updated_at')