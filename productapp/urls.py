from django.urls import path
from .views import show_products, ProductListCreateView, ProductDetailView, product_detail

urlpatterns = [
    path('show_products/' , show_products, name='show_products'),
    # Product detail page
    path('products/<int:pk>/', product_detail, name='product-detail'),
    
    # Category filtered view (optional - if you want separate URLs for categories)
    path('products/category/<str:category>/', show_products, name='products-by-category'),

    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
]