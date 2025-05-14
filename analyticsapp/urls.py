from django.urls import path
from . import views

urlpatterns = [
    path('sales/', views.sales_analytics, name='sales_analytics'),
    path('product-performance/', views.product_performance, name='product_performance'),
    path('customer-behavior/', views.customer_behavior, name='customer_behavior'),
    path('custom-chart/', views.custom_chart, name='custom_chart'),
    path('session-analytics/', views.session_analytics, name='session_analytics'),
]