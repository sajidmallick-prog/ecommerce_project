from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from . import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.show, name='home'),
    path('users/', include('usersapp.urls')),
    #  Add this redirect for old URLs
    path('usersapp/myAccount/', RedirectView.as_view(url='/users/myAccount/', permanent=True)),
    path('category/', include('categoriesapp.urls')), 
    path('supplier/', include('supplierapp.urls')),
    path('manufacturer/', include('manufacturerapp.urls')), 
    path('product/', include('productapp.urls')),  
    path('order/', include('orderapp.urls')),
    path('cart/', include('cartapp.urls')),
    path('payments/', include('paymentsapp.urls')),
    path('orderitem/', include('orderitemapp.urls')),
    path('reviews/', include('reviewsapp.urls')),
    path('wishlist/', include('wishlistapp.urls')),
  
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

