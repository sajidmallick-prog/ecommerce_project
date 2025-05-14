from rest_framework import serializers
from supplierapp.models import Supplier

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id','name','nationality','photo']

        