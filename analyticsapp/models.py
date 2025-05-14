from django.db import models
from django.contrib.auth import get_user_model
from productapp.models import Product
from orderapp.models import Order
from orderitemapp.models import OrderItem
from categoriesapp.models import Category

User = get_user_model()

class SalesSnapshot(models.Model):
    """Daily aggregated sales data"""
    date = models.DateField(unique=True)
    total_sales = models.DecimalField(max_digits=12, decimal_places=2)
    order_count = models.PositiveIntegerField()
    avg_order_value = models.DecimalField(max_digits=10, decimal_places=2)
    refunds = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Sales Snapshots"

    def __str__(self):
        return f"Sales on {self.date}"
    
class ProductPerformance(models.Model):
    """Daily product performance metrics"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date = models.DateField()
    views = models.PositiveIntegerField(default=0)
    cart_additions = models.PositiveIntegerField(default=0)
    purchases = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(max_digits=12, decimal_places=2)
    
    class Meta:
        ordering = ['-date', '-revenue']
        unique_together = [['product', 'date']]
        indexes = [
            models.Index(fields=['-date', 'revenue']),
        ]

    @property
    def conversion_rate(self):
        return (self.purchases / self.views * 100) if self.views > 0 else 0

    def __str__(self):
        return f"{self.product} on {self.date}"
    
class CustomerBehavior(models.Model):
    """Tracks user behavior patterns"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40)
    entry_point = models.CharField(max_length=200)
    first_product_view = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL, related_name='+')
    timestamp = models.DateTimeField(auto_now_add=True)
    converted = models.BooleanField(default=False)
    conversion_value = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    
    class Meta:
        verbose_name_plural = "Customer Behavior"
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['converted']),
        ]

    def __str__(self):
        return f"Behavior #{self.id}"
