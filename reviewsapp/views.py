from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from productapp.models import Product
from .models import Review

@login_required
def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    existing_review = Review.objects.filter(user=request.user, product=product).first()

    if request.method == 'POST':
        if existing_review:
            return JsonResponse({'error': 'You have already reviewed this product.'}, status=400)

        rating_input = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()

        try:
            rating = int(rating_input)
            if not (1 <= rating <= 5):
                raise ValueError("Invalid rating")
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Please select a valid rating between 1 and 5.'}, status=400)

        if not comment:
            return JsonResponse({'error': 'Comment cannot be empty.'}, status=400)

        review = Review.objects.create(
            user=request.user,
            product=product,
            rating=rating,
            comment=comment,
        )

        return JsonResponse({
            'message': 'Review submitted successfully.',
            'review': {
                'username': request.user.username,
                'rating': review.rating,
                'comment': review.comment,
            }
        })

    return render(request, 'reviewsapp/submit_review.html', {'product': product})
