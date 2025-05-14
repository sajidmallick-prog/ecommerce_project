from django.shortcuts import render
from supplierapp.models import Supplier
from rest_framework import generics
from .serializers import SupplierSerializer

def show_supplier(request):
    suppilers = Supplier.objects.all()
    return render(request, 'supplierapp/supplier.html', {'suppliers': suppilers}) 







class SupplierListCreation(generics.ListCreateAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

class SupplierDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


