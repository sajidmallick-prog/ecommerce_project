from django.db import models
from manufacturerapp.models import Manufacturer
from categoriesapp.models import Category
from supplierapp.models import Supplier

class Product(models.Model):
    product_name = models.CharField(max_length=255)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(upload_to='product_covers/', blank=True, null=True)
    # pdf_file = models.FileField(upload_to='product_pdfs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_name
