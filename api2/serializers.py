from rest_framework import serializers
from .models import Reel

class ReelSerializer(serializers.ModelSerializer):
    location = serializers.CharField(source='location.location_name')
    area = serializers.CharField(source='area.area_name')
    class Meta:
        model = Reel
        fields = '__all__'
