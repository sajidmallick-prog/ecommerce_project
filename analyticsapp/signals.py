from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from orderapp.models import Order, OrderItem
from productapp.models import ProductView
from .models import SalesSnapshot, ProductPerformance, CustomerJourney
from django.db.models import Sum, F, Count
from django.utils import timezone

@receiver(post_save, sender=Order)
def update_sales_snapshot(sender, instance, **kwargs):
    if instance.status == 'completed':
        today = timezone.now().date()
        
        # Get or create today's snapshot
        snapshot, created = SalesSnapshot.objects.get_or_create(date=today)
        
        # Recalculate all metrics
        completed_orders = Order.objects.filter(
            status='completed',
            created_at__date=today
        )
        
        snapshot.total_sales = completed_orders.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        snapshot.order_count = completed_orders.count()
        
        if snapshot.order_count > 0:
            snapshot.avg_order_value = snapshot.total_sales / snapshot.order_count
            
        snapshot.save()

@receiver(post_save, sender=OrderItem)
def update_product_performance(sender, instance, **kwargs):
    if instance.order.status == 'completed':
        product = instance.product
        today = timezone.now().date()
        
        # Get views from ProductView model (if exists)
        views = ProductView.objects.filter(
            product=product,
            timestamp__date=today
        ).count()
        
        # Update performance metrics
        perf, created = ProductPerformance.objects.get_or_create(
            product=product,
            date=today
        )
        
        perf.views = views
        perf.purchases = OrderItem.objects.filter(
            product=product,
            order__status='completed',
            order__created_at__date=today
        ).count()
        
        perf.revenue = OrderItem.objects.filter(
            product=product,
            order__status='completed',
            order__created_at__date=today
        ).aggregate(
            revenue=Sum(F('quantity') * F('price'))
        )['revenue'] or 0
        
        perf.save()