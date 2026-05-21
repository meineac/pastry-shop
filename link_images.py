import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pastry_shop.settings')
django.setup()

from catalog.models import Product
from django.conf import settings

def link_existing_images():
    products = Product.objects.all()
    linked_count = 0
    
    for product in products:
        # Generate the safe filename matching the existing files
        safe_name = "".join([c if c.isalnum() else "_" for c in product.name.lower()])
        filename = f"{safe_name}.jpg"
        
        # Define the relative path as it should be stored in the DB and the absolute path on disk
        relative_path = f"products/{filename}"
        absolute_path = os.path.join(settings.MEDIA_ROOT, 'products', filename)
        
        if os.path.exists(absolute_path):
            # Update the product record to point to the existing file
            product.photo.name = relative_path
            product.save(update_fields=['photo'])
            linked_count += 1
            print(f"Linked image for: {product.name}")
        else:
            print(f"File not found on disk for: {product.name} ({absolute_path})")
            
    print(f"\nSuccessfully linked {linked_count} images.")

if __name__ == '__main__':
    link_existing_images()