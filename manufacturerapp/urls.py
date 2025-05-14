from django.urls import path
from .views import ManufacturerListCreation, ManufacturerDetailView, show_manufacturer

urlpatterns = [
    path('show_manufacturers/', show_manufacturer, name='show_manufacturer'),
    path('manufacturers/', ManufacturerListCreation.as_view(), name='manufacturer-list-create'),
    path('manufacturers/<int:pk>/', ManufacturerDetailView.as_view(), name='manufacturer_details')
]