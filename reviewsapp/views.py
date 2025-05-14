from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from productapp.models import Product
from .models import Review
from reviewsapp.apps import ReviewsappConfig  # ensure it's correct

import logging
logger = logging.getLogger(__name__)

@login_required
def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    existing_review = Review.objects.filter(user=request.user, product=product).first()

    if request.method == 'POST':
        if existing_review:
            return JsonResponse({'error': 'You have already reviewed this product.'}, status=400)

        rating_input = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()

        logger.debug(f"Incoming rating: {rating_input}, comment: {comment}")

        try:
            rating = int(rating_input)
            if not (1 <= rating <= 5):
                raise ValueError("Invalid rating")
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Please select a valid rating between 1 and 5.'}, status=400)

        if not comment:
            return JsonResponse({'error': 'Comment cannot be empty.'}, status=400)

        try:
            if not ReviewsappConfig.vectorizer or not ReviewsappConfig.model:
                raise ValueError("Sentiment model not loaded.")

            logger.debug("Performing sentiment prediction...")
            vector = ReviewsappConfig.vectorizer.transform([comment])
            predicted = ReviewsappConfig.model.predict(vector)

            if not predicted.any():
                raise ValueError("Empty prediction result.")

            prediction = str(predicted[0]).lower()

            review = Review.objects.create(
                user=request.user,
                product=product,
                rating=rating,
                comment=comment,
                prediction=prediction
            )

            return JsonResponse({
                'message': 'Review submitted successfully.',
                'review': {
                    'username': request.user.username,
                    'rating': review.rating,
                    'comment': review.comment,
                    'prediction': review.prediction,
                }
            })

        except Exception as e:
            logger.exception("Prediction or review saving failed.")
            return JsonResponse({'error': f'Prediction failed: {str(e)}'}, status=500)

    return render(request, 'reviewsapp/submit_review.html', {'product': product})


def sentiment_counts(request, product_id):
    counts = Review.objects.filter(product_id=product_id).values('prediction').annotate(total=Count('id'))
    data = {"positive": 0, "neutral": 0, "negative": 0}

    for entry in counts:
        sentiment = entry["prediction"].lower()
        if sentiment in data:
            data[sentiment] = entry["total"]

    return JsonResponse(data)
