from django.shortcuts import render
from productapp.models import Product
from django.db.models import Avg

def show(request):
    products = Product.objects.all()
    products = Product.objects.order_by('-created_at')[:3]
    products = Product.objects.all().annotate(average_rating=Avg('review__rating'))
    return render(request, "home/index.html", {'products': products })