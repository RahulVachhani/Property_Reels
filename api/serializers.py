from .models import Reels
from rest_framework import serializers


class ReelSerializers(serializers.ModelSerializer):
    area = serializers.CharField(source="area.area_name")
    location = serializers.CharField(source='location.location_name')
    class Meta:
        model = Reels
        fields = '__all__'
    

    

