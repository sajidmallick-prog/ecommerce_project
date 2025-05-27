from django.shortcuts import render, redirect
from django.http import JsonResponse
from usersapp.models import User
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages, auth
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator

from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from .decoraters import custom_login_required
from orderapp.models import Order
import logging


logger = logging.getLogger(__name__)


@custom_login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_list.html', {'orders': orders}) 
    
# @login_required(login_url='customer_login')
def myAccount(request):
    return render(request, 'usersapp/myAccount.html', {
        'user': request.user,
    })


def activate(request, uidb64, token):              
    try:
        # Decode user ID from the URL
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Check if the user exists and the token is valid
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True  # Activate user
        user.save()
        messages.success(request, 'Congratulations! Your account has been activated.')
        return redirect('customer_login')  # Redirect to login page
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('customer_login')  # Redirect to login page if activation fails


def send_verification_email(request, user, mail_subject, email_template):
    """Function to send an email verification link"""
    try:
        current_site = get_current_site(request)
        message = render_to_string(email_template, {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        })
        to_email = user.email
        email = EmailMessage(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [to_email])
        email.content_subtype = "html"
        email.send()
        
        print(f"✅ Verification email sent to {to_email}")
    except Exception as e:
        print(f"❌ Email sending failed: {e}")



def admin_registration(request):
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            username = request.POST.get('username')
            dob = request.POST.get('dob')
            gender = request.POST.get('gender')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            profile_picture = request.FILES.get('profile_picture')

            # Debugging log to check the received data
            logger.debug(f"Received Data: {email}, {username}, {first_name}, {last_name}")

            # Ensure the data is valid
            if not email or not password or not username:
                return JsonResponse({'success': False, 'error': 'Missing required fields.'})

            # Create the User instance
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                dob=dob,
                gender=gender,
                phone=phone,
                address=address,
                profile_picture=profile_picture
            )

            # Set the user as admin
            user.is_staff = True  # Grant admin rights
            user.is_superuser = True  # Grant superuser rights
            user.user_type = 'admin'  # Optional if using a user_type field
            user.save()

            # Log in the user immediately after registration
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)

            # Return success response with redirect URL for the admin panel login
            return JsonResponse({
                'success': True, 
                'message': 'Registration successful!', 
                'redirect_url': '/admin/login/'
            })

        except Exception as e:
            logger.error(f"Error during registration: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})

    gender_choices = User._meta.get_field('gender').choices 
    return render(request, 'usersapp/admin_registration.html', {'gender_choices': gender_choices})


def customer_registration(request):
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            username = request.POST.get('username')
            dob = request.POST.get('dob')
            gender = request.POST.get('gender')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            profile_picture = request.FILES.get('profile_picture')  

            print(email, password, first_name, last_name, username, dob, gender, phone, address, profile_picture)

            # Create User instance with inactive status
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                username=username,
                dob=dob,
                gender=gender,
                phone=phone,
                address=address,
                profile_picture=profile_picture,
            )
            user.is_active = False  # User must verify email before activation
            user.user_type = 'customer'  # Ensure user_type is set to customer
            user.save()

            # Send verification email
            mail_subject = 'Activate your account'
            email_template = 'usersapp/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            return JsonResponse({'success': True, 'message': 'Registration successful!'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        
    gender_choices = User._meta.get_field('gender').choices
    return render(request, 'usersapp/customer_registration.html', {'gender_choices': gender_choices})


def customer_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            # Check if the user is a customer
            if user.user_type == 'customer':  # Ensure that the user is a customer
                login(request, user)
                
                # Check if the request is AJAX
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({"success": True, "redirect_url": "/users/myAccount/"})
                else:
                    return redirect('myAccount')
            else:
                # If the user is not a customer, show an error message
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({"success": False, "error": "Only customers are allowed to log in."})
                else:
                    messages.error(request, "Only customers are allowed to log in.")
                    return redirect('customer_login')

        else:
            # If authentication fails
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({"success": False, "error": "Invalid email or password."})
            else:
                messages.error(request, "Invalid email or password")
                return redirect('customer_login')

    return render(request, 'usersapp/customer_login.html')


def logout(request):
    auth.logout(request)
    messages.info(request, 'You are logged out.')
    return redirect('home')
    add_never_cache_headers(response)
    return response



from django.http import JsonResponse
from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import exceptions

from usersapp.authentication import JWTAuthentication, create_access_token, create_refresh_token, decode_refresh_token
from usersapp.models import User
from usersapp.serializers import UserSerializer

# User Registration through Class Based View
class RegisterAPIView(APIView):
    def post(self, request):
        data = request.data

        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('Passwords do not match!')

        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

# User Login
class LoginAPIView(APIView):
    def post(self, request: Request):
        email = request.data['email']
        password = request.data['password']
        user = User.objects.filter(email=email).first()
        if user is None:
            raise exceptions.AuthenticationFailed('Invalid credentials')

        if not user.check_password(password):
            raise exceptions.AuthenticationFailed('Invalid credentials')
        
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        response = Response()
        response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)
        response.data = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        return response

# Check Authenticated User
class UserAPIView(APIView):
    authentication_classes = [JWTAuthentication] # authentication_classes attribute is used to specify which Authentication is used

    def get(self, request):
        user = request.user
        is_admin = request.auth.get('is_admin', False)
        serializer = UserSerializer(user)
        return Response({
            'user': serializer.data,
            'is_admin': is_admin
        })

# Generate new Access token using Refresh token
# Access tokens usually have a short expiration time (e.g., 30 seconds).
# Instead of asking the user to log in again, we use a refresh token to generate a new access token.
class RefreshAPIView(APIView):
    def post(self, request: Request):
        refresh_token = request.COOKIES.get('refresh_token')
        id = decode_refresh_token(refresh_token)
        user = User.objects.get(pk=id)
        access_token = create_access_token(user.id)
        
        return Response({
            'user': UserSerializer(user).data,
            'access_token': access_token
        })

# User Logout through Class Based View
class LogoutAPIView(APIView):
    def post(self, request: Request):
        response: Response = Response()
        response.delete_cookie('refresh_token')
        response.data = {
            'message': 'success'
        }
        return response

# --------------------- Function Based View ---------------------
# User Registration through Function Based View
# def signup(request):
#     if request.method == 'POST':
#         data = request.POST
#         if data['password'] != data['password_confirm']:
#             raise exceptions.APIException('Passwords do not match!')

#         serializer = UserSerializer(data=data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return JsonResponse({'acknowledge': 'Check your email for Activation link!', 'success': True, 'response': serializer.data}, status=200)
#         # return Response(serializer.data)    
    
#     return render(request, 'account/user_register.html')

# # User Logout through Function Based View
# def api_logout(request):
#     response = Response()
#     response.delete_cookie('refresh_token')
#     response.data = {
#         'message': 'success'
#     }
#     return response