import os
import django
from django.test import Client
from django.conf import settings
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pastry_shop.settings')
django.setup()
settings.ALLOWED_HOSTS = ['*']

User = get_user_model()
user, created = User.objects.get_or_create(username='testuser')
if created:
    user.set_password('testpass')
    user.save()

client = Client(SERVER_NAME='localhost')
client.force_login(user)

urls = {
    "home": "/",
    "about": "/about/",
    "news": "/news/",
    "qna": "/qna/",
    "contacts": "/contacts/",
    "privacy": "/privacy-policy/",
    "vacancies": "/vacancies/",
    "reviews": "/reviews/",
    "promo_codes": "/promo-codes/",
    "cart": "/cart/",
    "checkout": "/checkout/",
}

os.makedirs("rendered_html", exist_ok=True)

for name, url in urls.items():
    response = client.get(url, follow=True)
    content = response.content.decode('utf-8')
    with open(f"rendered_html/{name}.html", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"{name} ({url}) - {response.status_code} - size: {len(content)}")
