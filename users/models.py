from django.core.exceptions import ValidationError
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

    def clean(self):
        super().clean()
        # 1. Superuser is always an ADMIN
        if self.is_superuser and self.role != self.Role.ADMIN:
            raise ValidationError({
                'role': "Superusers must always have the ADMIN role."
            })

        # 2. STAFF is STAFF and never a superuser
        if self.role == self.Role.STAFF and self.is_superuser:
            raise ValidationError({
                'is_superuser': "Staff users cannot be superusers."
            })

        # 3. CUSTOMER is CUSTOMER and never a superuser
        if self.role == self.Role.CUSTOMER and self.is_superuser:
            raise ValidationError({
                'is_superuser': "Customer users cannot be superusers."
            })

    def save(self, *args, **kwargs):
        # Enforce role logic:
        # 1. Superuser creation check: if a new superuser is created, promote to ADMIN
        if self.is_superuser and self.pk is None:
            self.role = self.Role.ADMIN

        # 2. ADMIN is always is_staff=True and is_superuser=True (set above on creation)
        if self.role == self.Role.ADMIN:
            self.is_staff = True

        # 3. STAFF: is_staff=True, is_superuser=False
        if self.role == self.Role.STAFF:
            self.is_superuser = False
            self.is_staff = True

        # 4. CUSTOMER: neither is_staff nor is_superuser
        if self.role == self.Role.CUSTOMER:
            self.is_superuser = False
            self.is_staff = False

        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

class CustomerProfile(TimestampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    date_of_birth = models.DateField(validators=[validate_age_18_plus])
    phone_number = models.CharField(
        max_length=20,
        validators=[phone_regex_validator],
        help_text="Format: +375 (29) XXX-XX-XX"
    )

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class StaffProfile(TimestampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    position = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='staff_photos/', null=True, blank=True)
    contact_details = models.TextField()
    date_of_birth = models.DateField(validators=[validate_age_18_plus])

    def __str__(self):
        return self.user.get_full_name() or self.user.username
