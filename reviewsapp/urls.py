from django.urls import path    
from .views import submit_review  # sentiment_counts


urlpatterns = [         
    path('submit/<int:product_id>/', submit_review, name='submit_review'),
    # path('sentiment_counts/<int:product_id>/', sentiment_counts, name='sentiment_counts'),
]