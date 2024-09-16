from rest_framework import serializers

from .models import *


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name"]


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["name"]

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        exclude = ('id','productline',)


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ("name","id")


class AttributeValueSerializer(serializers.ModelSerializer):
    attribute = AttributeSerializer(many=False)
    class Meta:
        model = AttributeValue
        fields = ("attribute","attribute_value",)


class ProductLineSerializer(serializers.ModelSerializer):
    product_image = ProductImageSerializer(many=True)
    attribute_value = AttributeValueSerializer(many=True)
    class Meta:
        model = ProductLine
        fields =(
            "price",
            "sku",
            "stock_qty",
            "order",
            "product_image",
            "attribute_value",
        )
    def to_representation(self, instance):
        data = super().to_representation(instance)
        av_data = data.pop("attribute_value")
        av_values = {}
        for key in av_data:
            av_values.update({key["attribute"]["id"]: key["attribute_value"]})
        data.update({"specification": av_values})
        return data


class ProductSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source="brand.name")
    category_name = serializers.CharField(source="category.name")
    product_line = ProductLineSerializer(many=True)
    attribute = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "name",
            "slug",
            "description",
            "is_digital",
            "brand_name",
            "category_name",
            "product_line",
            "attribute",
        )

    def get_attribute(self, obj):
        attribute = Attribute.objects.filter(product_type_attribute__product__id=obj.id)
        return AttributeSerializer(attribute, many=True).data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        av_data = data.pop("attribute")
        av_values = {}
        for key in av_data:
            av_values.update({key["id"]: key["name"]})
        data.update({"type specification": av_values})
        
        return data