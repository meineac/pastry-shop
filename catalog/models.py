from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit
from django.db import models
from core.models import TimestampedModel

class Category(TimestampedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Manufacturer(TimestampedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.name

class Product(TimestampedModel):
    class UnitMeasurement(models.TextChoices):
        PIECES = 'PCS', 'Pieces'
        KILOGRAMS = 'KG', 'Kilograms'
        LITERS = 'L', 'Liters'

    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    unit_of_measurement = models.CharField(
        max_length=3,
        choices=UnitMeasurement.choices,
        default=UnitMeasurement.PIECES
    )
    photo = models.ImageField(upload_to='products/', null=True, blank=True)
    photo_small = ImageSpecField(source='photo',
                                 processors=[ResizeToFit(300, 300)],
                                 format='JPEG',
                                 options={'quality': 85})
    photo_medium = ImageSpecField(source='photo',
                                  processors=[ResizeToFit(600, 600)],
                                  format='JPEG',
                                  options={'quality': 85})
    photo_large = ImageSpecField(source='photo',
                                 processors=[ResizeToFit(1200, 1200)],
                                 format='JPEG',
                                 options={'quality': 85})
    ingredients = models.TextField()
    is_active = models.BooleanField(default=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return self.name
