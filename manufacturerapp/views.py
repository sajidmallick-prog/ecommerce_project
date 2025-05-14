from django.shortcuts import render
from .models import Manufacturer
from rest_framework import generics
from manufacturerapp.serializers import ManufacturerSerializer

def show_manufacturer(request):
    manufacturers = Manufacturer.objects.all()
    return render(request, 'manufacturerapp/manufacturer.html', {'manufacturers': manufacturers}) 



class ManufacturerListCreation(generics.ListCreateAPIView):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer

class ManufacturerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer



