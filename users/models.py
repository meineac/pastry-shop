from django.db import models
from django.contrib.auth.models import AbstractUser
from core.models import TimestampedModel, phone_regex_validator, validate_age_18_plus

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        STAFF = 'STAFF', 'Staff'
        CUSTOMER = 'CUSTOMER', 'Customer'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.CUSTOMER
    )

    def __str__(self):
        return self.username

class CustomerProfile(TimestampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    name = models.CharField(max_length=255)
    date_of_birth = models.DateField(validators=[validate_age_18_plus])
    phone_number = models.CharField(
        max_length=20,
        validators=[phone_regex_validator],
        help_text="Format: +375 (29) XXX-XX-XX"
    )
    email = models.EmailField()

    def __str__(self):
        return self.name

class StaffProfile(TimestampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    full_name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='staff_photos/', null=True, blank=True)
    contact_details = models.TextField()
    date_of_birth = models.DateField(validators=[validate_age_18_plus])

    def __str__(self):
        return self.full_name
