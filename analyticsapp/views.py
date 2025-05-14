import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.shortcuts import render
from django.db.models import Sum, Count, Avg, Case, When, IntegerField, FloatField
from django.db.models.functions import TruncDay
from datetime import datetime, timedelta
from django.utils import timezone
from orderapp.models import Order
from productapp.models import Product
from reviewsapp.models import Review
from analyticsapp.models import CustomerBehavior, SalesSnapshot, ProductPerformance
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.sessions.models import Session

def staff_required(view_func):
    decorated_view = login_required(user_passes_test(
        lambda u: u.is_staff,
        login_url='/admin/login/'
    )(view_func))
    return decorated_view

def save_plot_to_base64(plt):
    """Helper function to save plot to base64 string"""
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
    plt.close()
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    return image_base64

@staff_required
def sales_analytics(request):
    # Time period selection (default last 30 days)
    time_period = int(request.GET.get('days', 30))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=time_period)

    # Query SalesSnapshot data
    sales_data = SalesSnapshot.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    ).order_by('date')

    # Prepare data for visualizations
    dates = [data.date.strftime('%m-%d') for data in sales_data]
    total_sales = [float(data.total_sales) for data in sales_data]
    order_counts = [data.order_count for data in sales_data]
    refunds = [float(data.refunds) for data in sales_data]

    # 1. Sales Trend Line Chart
    plt.figure(figsize=(12, 6))
    plt.plot(dates, total_sales, 'g-', linewidth=2, label='Total Sales')
    plt.fill_between(dates, total_sales, color='green', alpha=0.1)
    plt.title(f'Sales Trend (Last {time_period} Days)')
    plt.xlabel('Date')
    plt.ylabel('Sales Amount ($)')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    sales_trend = save_plot_to_base64(plt)

    # 2. Order Count Bar Chart
    plt.figure(figsize=(12, 6))
    plt.bar(dates, order_counts, color='blue', alpha=0.7)
    plt.title(f'Order Count by Day (Last {time_period} Days)')
    plt.xlabel('Date')
    plt.ylabel('Number of Orders')
    plt.xticks(rotation=45)
    plt.grid(True, axis='y')
    order_count_chart = save_plot_to_base64(plt)

    # 3. Refund Proportion Pie Chart
    total_sales_sum = sum(total_sales)
    total_refunds_sum = sum(refunds)
    if total_sales_sum > 0 or total_refunds_sum > 0:
        plt.figure(figsize=(8, 8))
        labels = ['Net Sales', 'Refunds']
        sizes = [total_sales_sum - total_refunds_sum, total_refunds_sum]
        colors = ['#66b3ff', '#ff9999']
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        plt.title('Sales vs. Refunds Proportion')
        refund_pie = save_plot_to_base64(plt)
    else:
        refund_pie = None

    return render(request, 'analyticsapp/sales.html', {
        'sales_trend': sales_trend,
        'order_count_chart': order_count_chart,
        'refund_pie': refund_pie,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'time_period': time_period,
    })

@staff_required
def product_performance(request):
    # Top selling products
    top_products = Product.objects.annotate(
        total_sold=Sum('orderitem__quantity')
    ).order_by('-total_sold')[:10]
    
    product_names = [p.product_name[:15] + '...' for p in top_products]
    quantities = [p.total_sold or 0 for p in top_products]
    
    plt.figure(figsize=(10, 6))
    bars = plt.barh(product_names, quantities, color='skyblue')
    plt.bar_label(bars, padding=3)
    plt.title('Top Selling Products')
    plt.xlabel('Quantity Sold')
    plt.tight_layout()
    
    top_products_chart = save_plot_to_base64(plt)
    
    # Product ratings distribution
    ratings = Review.objects.values('rating').annotate(
        count=Count('id')
    ).order_by('rating')
    
    return render(request, 'analyticsapp/product_performance.html', {
        'top_products_chart': top_products_chart,
        'top_products': top_products,
    })

@staff_required
def customer_behavior(request):
    # Customer segmentation analysis
    from django.db.models import Count, Case, When, IntegerField
    
    # Example: Customer purchase frequency
    customer_data = Order.objects.filter(
        status='completed'
    ).values('user').annotate(
        order_count=Count('id'),
        total_spent=Sum('total_price')
    ).order_by('-total_spent')[:10]
    
    # Generate chart
    plt.figure(figsize=(10, 6))
    customers = [f"Customer {d['user']}" for d in customer_data]
    spending = [float(d['total_spent']) for d in customer_data]
    
    plt.barh(customers, spending, color='purple')
    plt.title('Top Customers by Spending')
    plt.xlabel('Total Amount Spent')
    plt.tight_layout()
    
    behavior_chart = save_plot_to_base64(plt)
    
    return render(request, 'analyticsapp/customer_behavior.html', {
        'behavior_chart': behavior_chart
    })

@staff_required
def custom_chart(request):
    if request.method == 'POST':
        # Handle form submission for custom chart parameters
        chart_type = request.POST.get('chart_type')
        date_range = request.POST.get('date_range')
        
        # Generate chart based on parameters
        if chart_type == 'category_sales':
            # Implement category sales chart
            pass
        elif chart_type == 'payment_methods':
            # Implement payment methods chart
            pass
            
    return render(request, 'analyticsapp/custom_chart.html')

@staff_required
def session_analytics(request):
    # Time period selection (default last 7 days)
    time_period = int(request.GET.get('days', 7))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=time_period)
    
    # Basic session metrics
    session_metrics = {
        'total_sessions': CustomerBehavior.objects.filter(
            timestamp__gte=start_date
        ).count(),
        'unique_visitors': CustomerBehavior.objects.filter(
            timestamp__gte=start_date
        ).values('session_key').distinct().count(),
        'returning_visitors': CustomerBehavior.objects.filter(
            timestamp__gte=start_date
        ).values('session_key').annotate(
            visit_count=Count('id')
        ).filter(visit_count__gt=1).count(),
        'conversion_rate': CustomerBehavior.objects.filter(
            timestamp__gte=start_date
        ).aggregate(
            rate=Avg(
                Case(
                    When(converted=True, then=1),
                    default=0,
                    output_field=FloatField()
                )
            )
        )['rate'] * 100 if CustomerBehavior.objects.filter(timestamp__gte=start_date).exists() else 0,
    }

    # Session trend by day
    sessions_by_day = CustomerBehavior.objects.filter(
        timestamp__gte=start_date
    ).annotate(
        day=TruncDay('timestamp')
    ).values('day').annotate(
        count=Count('id'),
        conversions=Sum(Case(
            When(converted=True, then=1),
            default=0,
            output_field=IntegerField()
        ))
    ).order_by('day')

    # Entry point analysis
    entry_points = CustomerBehavior.objects.filter(
        timestamp__gte=start_date
    ).values('entry_point').annotate(
        count=Count('id'),
        converted=Sum(Case(
            When(converted=True, then=1),
            default=0,
            output_field=IntegerField()
        ))
    ).order_by('-count')[:10]

    # Prepare charts
    days = [s['day'].strftime('%m-%d') for s in sessions_by_day]
    counts = [s['count'] for s in sessions_by_day]
    conversions = [s['conversions'] for s in sessions_by_day]

    # Session trend chart
    plt.figure(figsize=(12, 6))
    plt.plot(days, counts, 'b-', label='Sessions')
    plt.plot(days, conversions, 'g-', label='Conversions')
    plt.fill_between(days, counts, color='blue', alpha=0.1)
    plt.title(f'Session Trend (Last {time_period} Days)')
    plt.xlabel('Date')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    session_trend = save_plot_to_base64(plt)

    # Entry points chart
    sources = [e['entry_point'][:30] + '...' if len(e['entry_point']) > 30 else e['entry_point'] 
               for e in entry_points]
    source_counts = [e['count'] for e in entry_points]
    
    plt.figure(figsize=(10, 6))
    plt.barh(sources[::-1], source_counts[::-1], color='teal')
    plt.title('Top Entry Points')
    plt.xlabel('Sessions')
    entry_chart = save_plot_to_base64(plt)

    return render(request, 'analyticsapp/session_analytics.html', {
        'session_metrics': session_metrics,
        'session_trend': session_trend,
        'entry_chart': entry_chart,
        'entry_points': entry_points,
        'time_period': time_period,
        'start_date': start_date.date(),
        'end_date': end_date.date(),
    })