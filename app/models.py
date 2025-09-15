from django.db import models
from multiselectfield import MultiSelectField

class Color(models.Model):
    name = models.CharField(max_length=255, verbose_name="Color")  # use name, not color/image combo
    image = models.ImageField(upload_to='color/', blank=True, null=True)

    def __str__(self):
        return self.name  # admin will display the color name in checkbox

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('almirah', 'Almirah'),
        ('beds', 'Beds'),
        ('chairs', 'Chairs'),
        ('dining', 'Dining'),
        ('mattress', 'Mattress'),
        ('sofa', 'Sofa'),
        ('table', 'Table'),
        ('safe', 'Safe'),
    ]

    TAG_CHOICES = [
        ('offers', 'Offers'),
        ('new_arrivals', 'New Arrivals'),
        ('best_sellers', 'Best Sellers'),
    ]

    name = models.CharField(max_length=255)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, blank=True)
    tags = MultiSelectField(choices=TAG_CHOICES, blank=True)
    features = models.TextField(blank=True)
    colors = models.ManyToManyField(Color, blank=True, related_name='products')  # This will be checkboxes
    materials = models.CharField(max_length=255, blank=True)
    measurements = models.CharField(max_length=255, blank=True)
    is_in_stock = models.BooleanField(default=True)
    delivery_availability = models.TextField(blank=True)

    def discount_rate(self):
        if self.discounted_price:
            return round(100 - (self.discounted_price / self.original_price * 100), 2)
        return None

    def __str__(self):
        return self.name



class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"{self.product.name}"
