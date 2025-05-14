from django.urls import path
from .views import SupplierListCreation, SupplierDetailView, show_supplier

urlpatterns = [
    path('show_suppliers/', show_supplier, name='show_supplier'),
    path('suppliers/', SupplierListCreation.as_view(), name='Supplier-list-create'),
    path('suppliers/<int:pk>/', SupplierDetailView.as_view(), name='Supplier_details'),
]