from django.shortcuts import render, get_object_or_404, redirect
import razorpay
import time
import requests.exceptions
from django.http import JsonResponse

from ecommerce_final import settings
from orderapp.models import Order
from .models import Payment
from productapp.models import Product
from cartapp.models import Cart
from orderitemapp.models import OrderItem
from usersapp.decoraters import custom_login_required
from django.db.models import F
from django.db import transaction
from django.core.mail import EmailMessage
from django.conf import settings
import os

# Razorpay client initialization
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def payment(request):
    amount = request.POST.get("amount")
    return render(request, "paymentsapp/payment.html", {"amount": amount})


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orderapp/order_success.html', {'order': order})


@custom_login_required
def create_order(request):
    if request.method == 'POST':
        try:
            amount = int(float(request.POST.get("amount", 0)))  
            
            if not amount or amount <= 0:
                return JsonResponse({
                    "status": "error",
                    "message": "Invalid amount provided"
                }, status=400)

            # Create Razorpay order
            order_response = client.order.create({
                "amount": amount,
                "currency": "INR",
                "payment_capture": 1
            })

            # Create database records
            order = Order.objects.create(
                user=request.user,
                total_price=amount / 100,
                razorpay_order_id=order_response['id']
            )

            Payment.objects.create(
                user=request.user,
                order=order,
                amount=amount / 100,
                payment_method='Razorpay',
                status='Pending',
                transaction_id=order_response['id']
            )

            return JsonResponse({
                "status": "success",
                "key": settings.RAZORPAY_KEY_ID,  # Ensure this is at top level
                "order_id": order_response['id'],
                "amount": amount,
                "currency": "INR",
                "name": "Pshop",
                "description": "Order Payment",
                "prefill": {
                    "name": request.user.get_full_name(),
                    "email": request.user.email
                },
                "order_id_db": order.id
            })
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            }, status=500)
    return JsonResponse({
        "status": "error",
        "message": "Invalid request method"
    }, status=405)

@custom_login_required
def verify_payment(request):
    if request.method == "POST":
        try:
            data = request.POST
            print("Received Data: ", data)

            razorpay_order_id = data.get("razorpay_order_id")
            razorpay_payment_id = data.get("razorpay_payment_id")
            razorpay_signature = data.get("razorpay_signature")

            if not (razorpay_order_id and razorpay_payment_id and razorpay_signature):
                return JsonResponse({"error": "Missing required payment details."})

            # 1. Verify the Razorpay signature
            params_dict = {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            }

            client.utility.verify_payment_signature(params_dict)
            print("✅ Payment verification successful!")

            # 2. Mark payment and order as complete
            payment = Payment.objects.get(transaction_id=razorpay_order_id)
            payment.status = 'Completed'
            payment.is_paid = True
            payment.save()

            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
            order.status = 'Completed'
            order.save()



            # Inside the try block and within transaction.atomic():

            with transaction.atomic():
                if request.user.is_authenticated:
                    # 1. Cart-based purchase
                    active_cart_items = Cart.objects.filter(user=request.user, is_active=True)

                    if active_cart_items.exists():
                        for cart_item in active_cart_items:
                            product = cart_item.product
                            quantity = cart_item.quantity

                            if product.stock >= quantity:
                                product.stock -= quantity
                                product.save()
                            else:
                                return JsonResponse({
                                    "error": f"Insufficient stock for product: {product.product_name}"
                                })

                        active_cart_items.delete()
                        print("🧹 Purchased items deleted from cart!")

                    # 2. Direct purchase (product_id sent via POST)
                    else:
                        product_id = request.POST.get("product_id")
                        category_id = request.POST.get("category_id")
                        quantity = int(request.POST.get("quantity", 1))

                        if product_id and category_id:
                            product = get_object_or_404(Product, id=product_id, category_id=category_id)

                            if product.stock >= quantity:
                                product.stock -= quantity
                                product.save()
                                print(f"📦 Direct purchase: stock updated for {product.product_name}")
                            else:
                                return JsonResponse({
                                    "error": f"Insufficient stock for product: {product.product_name}"
                                })
                        else:
                            return JsonResponse({"error": "Missing product info for direct purchase."})


            return JsonResponse({
                "success": True,
                "message": "Payment verified and all items processed.",
                "order_id": order.id
            })
    
        except razorpay.errors.SignatureVerificationError:
            print("❌ Signature verification failed!")
            return JsonResponse({"error": "Invalid payment signature."})

        except Exception as e:
            print("⚠️ Error:", str(e))
            return JsonResponse({"error": str(e)})

    return JsonResponse({"error": "Invalid request method"})



