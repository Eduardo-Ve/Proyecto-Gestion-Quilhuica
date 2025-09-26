from django.db import models


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name_cat = models.CharField(max_length=120)
    description_cat = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'CATEGORY'
        ordering = ['name_cat']

    def __str__(self):
        return self.name_cat


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name_prod = models.CharField(max_length=120)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        db_column='category_id',
        related_name='products',
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'PRODUCT'
        ordering = ['name_prod']

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

    presentation_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        db_column='product_id',
        related_name='presentations',
    )
    package_type = models.CharField(max_length=10, choices=PACKAGE_CHOICES)
    content_value = models.FloatField()
    content_unit = models.CharField(max_length=10, choices=UNIT_CHOICES)

    class Meta:
        db_table = 'PRESENTATION'
        ordering = ['product__name_prod', 'package_type']

    def __str__(self):
        return f'{self.product} - {self.package_type} {self.content_value} {self.content_unit}'

