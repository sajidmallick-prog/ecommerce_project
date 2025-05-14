from rest_framework import serializers
from .models import Manufacturer

class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        models = Manufacturer
        fields = ['id', 'name','address','contact','website']