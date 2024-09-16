from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import *
from .serializers import *


class CategoryViewSet(viewsets.ViewSet):
    """
    Viewset or viewing all categories
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def list(self, request):
        serializers = CategorySerializer(self.queryset, many=True)
        return Response(serializers.data)


class BrandViewSet(viewsets.ViewSet):
    """
    Viewset or viewing all categories
    """

    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

    def list(self, request):
        serializers = BrandSerializer(self.queryset, many=True)
        return Response(serializers.data)


class ProductViewSet(viewsets.ViewSet):
    """
    Viewset or viewing all categories
    """

    queryset = Product.objects.all().isactive()
    serializer_class = ProductSerializer
    lookup_field = "slug"

    def retrieve(self, request, slug=None):
        serializers = ProductSerializer(
            Product.objects.filter(slug=slug)
            .select_related("category", "brand")
            .prefetch_related("product_line__product_image")
            .prefetch_related("product_line__attribute_value__attribute"),
            many=True,
        )
        return Response(serializers.data)

    def list(self, request):
        serializers = ProductSerializer(self.queryset, many=True)
        return Response(serializers.data)

    @action(
        methods=[
            "get",
        ],
        detail=False,
        url_path="category/(?P<category>\w+)/all",
    )
    def list_products_by_category(self, request, category=None):
        """
        An endpoint to return products by category
        """
        serializers = ProductSerializer(
            self.queryset.filter(category__name=category), many=True
        )
        return Response(serializers.data)
