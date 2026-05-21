import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pastry_shop.settings')
django.setup()

from catalog.models import Product
from cms.models import News
from users.models import StaffProfile
from django.conf import settings

def link_existing_images():
    # 1. Link Product Images
    products = Product.objects.all()
    linked_count = 0
    
    for product in products:
        safe_name = "".join([c if c.isalnum() else "_" for c in product.name.lower()])
        filename = f"{safe_name}.jpg"
        
        relative_path = f"products/{filename}"
        absolute_path = os.path.join(settings.MEDIA_ROOT, 'products', filename)
        
        if os.path.exists(absolute_path):
            product.photo.name = relative_path
            product.save(update_fields=['photo'])
            linked_count += 1
            print(f"Linked image for product: {product.name}")
        else:
            print(f"File not found on disk for product: {product.name} ({absolute_path})")
            
    print(f"\nSuccessfully linked {linked_count} product images.\n")

    # 2. Link News Images
    news_items = News.objects.all()
    news_linked_count = 0
    
    # Replace the News loop in link_images.py with this:
    for news in news_items:
        # Convert spaces/hyphens to underscores and remove other special characters
        clean_name = news.title.lower().replace(' ', '_').replace('-', '_')
        safe_name = "".join([c if c.isalnum() or c == '_' else "" for c in clean_name])
        filename = f"{safe_name}.jpg"
    
        relative_path = f"news/{filename}"
        absolute_path = os.path.join(settings.MEDIA_ROOT, 'news', filename)
        
        if os.path.exists(absolute_path):
            news.image.name = relative_path
            news.save(update_fields=['image'])
            news_linked_count += 1
            print(f"Linked image for news: {news.title}")
        else:
            print(f"File not found on disk for news: {news.title} ({absolute_path})")
            
    print(f"\nSuccessfully linked {news_linked_count} news images.\n")

    # 3. Link Staff Images
    staff_profiles = StaffProfile.objects.all()
    staff_linked_count = 0

    for staff in staff_profiles:
        # Assuming images are named after the username (e.g., staffuser1.jpg)
        safe_name = "".join([c if c.isalnum() else "_" for c in staff.user.username.lower()])
        filename = f"{safe_name}.jpg"
        
        relative_path = f"staff_photos/{filename}"
        absolute_path = os.path.join(settings.MEDIA_ROOT, 'staff_photos', filename)

        if os.path.exists(absolute_path):
            staff.photo.name = relative_path
            staff.save(update_fields=['photo'])
            staff_linked_count += 1
            print(f"Linked image for staff: {staff.user.username}")
        else:
            print(f"File not found on disk for staff: {staff.user.username} ({absolute_path})")

    print(f"\nSuccessfully linked {staff_linked_count} staff images.")

if __name__ == '__main__':
    link_existing_images()