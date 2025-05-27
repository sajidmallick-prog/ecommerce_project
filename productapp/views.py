from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Category
from orderapp.models import Order
from usersapp.decoraters import custom_login_required
from django.core.paginator import Paginator
from rest_framework import generics
from .serializers import ProductSerializer
from django.db.models import Avg


from django.db.models import Avg
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Product, Category

def show_products(request, category=None):
    # Get base queryset with ordering to fix UnorderedObjectListWarning
    products = Product.objects.all().annotate(average_rating=Avg('review__rating')).order_by('id')  # or any suitable field
    
    # Filter by category if specified (either through URL or query parameter)
    category_filter = category or request.GET.get('category')
    if category_filter:
        products = products.filter(category__name__iexact=category_filter)
    
    # Paginate products
    paginator = Paginator(products, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    # Get featured products for category sections
    categories = ['Men', 'Women', 'Kids', 'Accessories']
    category_products = {}
    
    for cat in categories:
        category_products[f"{cat.lower()}_products"] = Product.objects.filter(
            category__name__iexact=cat
        ).annotate(average_rating=Avg('review__rating')).order_by('-id')[:4]  # recent 4 items
    
    context = {
        "page_obj": page_obj,
        **category_products,
        "categories": Category.objects.all(),
        "current_category": category_filter
    }
    
    return render(request, "productapp/products.html", context)

  
    # products = Product.objects.all()
    # products = Product.objects.all().annotate(average_rating=Avg('review__rating'))
    # paginator = Paginator(products, 6)  
    # page_number = request.GET.get("page")
    # page_obj = paginator.get_page(page_number)

    # return render(request, "productapp/products.html", {"page_obj": page_obj})


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# Retrieve, Update, and Delete View
class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

