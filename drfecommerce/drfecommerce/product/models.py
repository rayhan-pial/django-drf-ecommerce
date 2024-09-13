from typing import Collection
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from .fields import *
from django.core.exceptions import ValidationError


class ActiveQueryset(models.QuerySet):
    def isactive(self):
        return self.filter(is_active=True)


class Category(MPTTModel):
    name = models.CharField(max_length=100)
    parent = TreeForeignKey("self", on_delete=models.PROTECT, null=True, blank=True)
    is_active = models.BooleanField(default=False)

    objects = ActiveQueryset.as_manager()

    class MPTTMeta:
        order_insertion_by = ["name"]

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)

    objects = ActiveQueryset.as_manager()

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True)
    is_digital = models.BooleanField(default=False)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = TreeForeignKey(
        "Category", on_delete=models.SET_NULL, null=True, blank=True
    )
    is_active = models.BooleanField(default=False)

    objects = ActiveQueryset.as_manager()

    def __str__(self):
        return self.name


class ProductLine(models.Model):
    price = models.DecimalField(decimal_places=2, max_digits=5)
    sku = models.CharField(max_length=100)
    stock_qty = models.IntegerField()
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_line"
    )
    is_active = models.BooleanField(default=False)
    order = OrderField(unique_for_field="product", blank=True)
    objects = ActiveQueryset.as_manager()

    # Easy approach --------------- ( i )
    # order = models.PositiveIntegerField(blank=True, null=True)


    # def clean_fields(self, exclude= None):
    #     super().clean_fields(exclude=exclude)
    #     qs = ProductLine.objects.filter(product=self.product)
    #     for obj in qs:
    #         if self.id != obj.id and self.order ==obj.order:
    #             raise ValidationError("Duplicate value.")

    def save(self, *args, **kwargs):
        if ProductLine.objects.filter(product=self.product, order=self.order).exists():
            raise ValidationError("A ProductLine with this order already exists for this product.")

        return super(ProductLine, self).save(*args, **kwargs)


    # Easy approach --------------- ( i )
    # def save(self, *args, **kwargs):
    #     # Ensure the 'order' field is unique for each product
    #     if self.order is None:  # If 'order' is not provided
    #         # Get the highest 'order' value for the product
    #         last_product_line = ProductLine.objects.filter(product=self.product).order_by('-order').first()
    #         if last_product_line:
    #             # Set 'order' to the next highest value
    #             self.order = last_product_line.order + 1
    #         else:
    #             # If no ProductLine exists for the product, set 'order' to 1
    #             self.order = 1
    #     else:
    #         # Ensure 'order' is unique within the same product
    #         if ProductLine.objects.filter(product=self.product, order=self.order).exists():
    #             raise ValueError("A ProductLine with this order already exists for this product.")

    #     super().save(*args, **kwargs)  # Call the base class save method

    def __str__(self):
        return str(self.sku)


class ProductImage(models.Model):
    alternative_text = models.CharField(max_length=100)
    url = models.ImageField(upload_to=None,default="test.jpg")
    productline = models.ForeignKey(
        ProductLine, on_delete=models.CASCADE, related_name="product_image"
    )
    order = OrderField(unique_for_field="productline", blank=True)


    def save(self, *args, **kwargs):
        if ProductImage.objects.filter(productline=self.productlined, order=self.order).exists():
            raise ValidationError("A ProductLine with this order already exists for this product.")

        return super(ProductImage, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.order)