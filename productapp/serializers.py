from rest_framework import serializers
from .models import Product
from supplierapp.models import Supplier
from categoriesapp.models import Category
from manufacturerapp.models import Manufacturer

class ProductSerializer(serializers.ModelSerializer):
    supplier = serializers.StringRelatedField()  # Returns suplliers name instead of ID
    manufacturer = serializers.StringRelatedField()  # Returns manufacturers name instead of ID
    category = serializers.StringRelatedField()  # Returns category's name instead of ID

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'supplier', 'manufacturer', 'category', 'price', 'stock', 'description', 'cover_image', 'created_at']
