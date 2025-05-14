from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from productapp.models import Product, Category
from .models import Order
from usersapp.decoraters import custom_login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from orderitemapp.models import OrderItem
from cartapp.models import Cart
from django.views.decorators.csrf import csrf_protect


@custom_login_required
@csrf_protect
def payment(request):
    if request.method == "POST":
        amount = request.POST.get("amount", "0.00")
        product_id = request.POST.get("product_id")
        category_id = request.POST.get("category_id")
        
        try:
            quantity = int(request.POST.get("quantity") or 1)
        except ValueError:
            quantity = 1

        return render(request, "paymentsapp/payment.html", {
            "amount": amount,
            "product_id": product_id,
            "category_id": category_id,
            "quantity": quantity
        })
    else:
        return render(request, "paymentsapp/payment.html", {"amount": "0.00"})

# This FBV will be called when the user clicks on the "Place Order" button for a product
@custom_login_required
def order_form(request, product_id, category_id):
    product = get_object_or_404(Product, id=product_id, category_id=category_id)
    quantity_range = range(1, product.stock + 1) if product.stock > 0 else range(1)

    if request.method == "POST":
        try:
            quantity = int(request.POST.get("quantity", 1))
            total_price = request.POST.get("total_price")

            if product.stock < quantity:
                return JsonResponse({"message": "Not enough stock available!"}, status=400)

            # If price not received from frontend
            if not total_price:
                total_price = product.price * quantity + 70 # Adding shipping cost
            else:
                total_price = float(total_price)            

            return JsonResponse({
                "status": "success",
                "message": "Stock updated successfully!",
                "total_price": total_price,
                "product_id": product.id,
                "category_id": category_id,
                "quantity": quantity
            })

        except Exception as e:
            return JsonResponse({"message": f"Error processing request: {str(e)}"}, status=400)

    context = {
        'product': product,
        'quantity_range': quantity_range
    }
    return render(request, 'orderapp/add_order.html', context)

# order from  cart
@custom_login_required
def order_form_cart(request):
    cart_items = Cart.objects.filter(user=request.user, is_active=True)
    total_item_count = cart_items.count()
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    total_price += 70 

    print("Total Price: ", total_price)
    print("Total Items in Cart: ", total_item_count)

    if request.method == "POST":
        try:
            quantity = int(request.POST.get("quantity", 1))
            total_price = request.POST.get("total_price")

            return JsonResponse({
                "status": "success",
                "message": "Stock updated successfully!",
                "total_price": total_price,
                "quantity": quantity
            })

        except Exception as e:
            return JsonResponse({"message": f"Error processing request: {str(e)}"}, status=400)

    return render(request, 'orderapp/add_order.html')

@custom_login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orderapp/order_list.html', {'orders': orders})    

@custom_login_required
def download_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = OrderItem.objects.filter(order=order)
    for item in items:
        item.total_price = item.quantity * item.price_at_purchase

    
    template_path = 'orderapp/order_pdf.html'
    context = {'order': order, 'items': items}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="order_{order_id}.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF: <pre>' + html + '</pre>')
    return response 










from rest_framework import generics
from .models import Order
from .serializers import OrderSerializer

# List and Create Orders
class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

# Retrieve, Update, and Delete Order
class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

