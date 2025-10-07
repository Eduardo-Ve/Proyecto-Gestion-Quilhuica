from django.db import models

class Category(models.Model):
    name_cat = models.CharField(max_length=100, unique=True)
    description_cat = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name_cat


class Product(models.Model):
    name_prod = models.CharField(max_length=150, unique=True)
    added_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name_prod


class Presentation(models.Model):
    PACKAGE_CHOICES = [
        ('sack', 'Sack'),
        ('drum', 'Drum'),
        ('box', 'Box'),
        ('package', 'Package'),
    ]
    UNIT_CHOICES = [
        ('kg', 'Kilograms'),
        ('liters', 'Liters'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    package_type = models.CharField(max_length=20, choices=PACKAGE_CHOICES)
    content_value = models.FloatField()
    content_unit = models.CharField(max_length=10, choices=UNIT_CHOICES)

    def __str__(self):
        return f"{self.product.name_prod} - {self.content_value} {self.content_unit}"
