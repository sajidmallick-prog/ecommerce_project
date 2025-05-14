from django.db import models

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name