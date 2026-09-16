"""
Image-linking helpers for seed commands.

Each function scans the media directory for pre-existing image files
and links them to the corresponding database records.
"""

import os

from django.conf import settings


def link_product_images(stdout):
    """Link product images from media/products/ to Product records."""
    from catalog.models import Product

    products = Product.objects.all()
    linked = 0

    for product in products:
        safe_name = "".join(
            c if c.isalnum() else "_" for c in product.name.lower()
        )
        filename = f"{safe_name}.jpg"
        absolute_path = os.path.join(settings.MEDIA_ROOT, "products", filename)

        if os.path.exists(absolute_path):
            product.photo.name = f"products/{filename}"
            product.save(update_fields=["photo"])
            linked += 1
        else:
            stdout.write(f"  Image not found for product: {product.name}")

    stdout.write(f"  Linked {linked} product image(s).")
    return linked


def link_news_images(stdout):
    """Link news images from media/news/ to News records."""
    from cms.models import News

    news_items = News.objects.all()
    linked = 0

    for news in news_items:
        clean_name = news.title.lower().replace(" ", "_").replace("-", "_")
        safe_name = "".join(
            c if c.isalnum() or c == "_" else "" for c in clean_name
        )
        filename = f"{safe_name}.jpg"
        absolute_path = os.path.join(settings.MEDIA_ROOT, "news", filename)

        if os.path.exists(absolute_path):
            news.image.name = f"news/{filename}"
            news.save(update_fields=["image"])
            linked += 1
        else:
            stdout.write(f"  Image not found for news: {news.title}")

    stdout.write(f"  Linked {linked} news image(s).")
    return linked


def link_staff_images(stdout):
    """Link staff photos from media/staff_photos/ to StaffProfile records."""
    from users.models import StaffProfile

    profiles = StaffProfile.objects.select_related("user").all()
    linked = 0

    for staff in profiles:
        safe_name = "".join(
            c if c.isalnum() else "_" for c in staff.user.username.lower()
        )
        filename = f"{safe_name}.jpg"
        absolute_path = os.path.join(
            settings.MEDIA_ROOT, "staff_photos", filename
        )

        if os.path.exists(absolute_path):
            staff.photo.name = f"staff_photos/{filename}"
            staff.save(update_fields=["photo"])
            linked += 1
        else:
            stdout.write(
                f"  Image not found for staff: {staff.user.username}"
            )

    stdout.write(f"  Linked {linked} staff image(s).")
    return linked
