from django.contrib import admin
from .models import Product, ProductImage,Color

class ProductImageInline(admin.TabularInline):  # Inline so images show inside Product
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "original_price", "discounted_price", "discount_rate")
    search_fields = ("name", "features")
    list_filter = ("category", "tags", "colors")
    filter_horizontal = ("colors",)
    inlines = [ProductImageInline]  # Show images inside product admin

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "image")

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("name", "image")

