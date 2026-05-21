"""
URL configuration for pastry_shop project.
"""

from django.contrib import admin
from django.conf import settings
from django.views.static import serve
from django.urls import re_path, include

urlpatterns = [
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^", include("core.urls", namespace="core")),
    re_path(r"^", include("cms.urls", namespace="cms")),
    re_path(r"^", include("users.urls")),
    re_path(r"^", include("catalog.urls", namespace="catalog")),
    re_path(r"^", include("purchasing.urls", namespace="purchasing")),
]

# ---------------------------------------------------------------------------
# Media file serving
# ---------------------------------------------------------------------------
# Django does NOT serve media files automatically in any mode.
# We wire up django.views.static.serve unconditionally so that uploaded images
# (products, news, staff photos) work both in local development and on Render's
# free tier (which has no object-storage / CDN).
#
# In a production deployment with a dedicated object-storage service (S3, GCS,
# Cloudinary, etc.) you would remove this and configure DEFAULT_FILE_STORAGE
# instead.  For Render free tier without paid storage this is the correct
# approach.
# ---------------------------------------------------------------------------
urlpatterns += [
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
]
