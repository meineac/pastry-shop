"""
Test settings for Pastry Shop.

Overrides production security settings that break the test client
(SECURE_SSL_REDIRECT causes 301 redirects instead of 200 responses).

Usage: python manage.py test --settings=pastry_shop.test_settings
"""
from .settings import *  # noqa: F401, F403

# Disable HTTPS redirect so the test client gets real responses
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0

# Use fast password hasher to speed up tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

