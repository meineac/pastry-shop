from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path, include

urlpatterns = [
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^", include("core.urls", namespace="core")),
    re_path(r"^", include("cms.urls", namespace="cms")),
    re_path(r"^", include("users.urls")),
    re_path(r"^", include("catalog.urls", namespace="catalog")),
    re_path(r"^", include("purchasing.urls", namespace="purchasing")),
]

# Media file serving — only active during development (DEBUG=True).
# In production, media should be served by Nginx, a CDN, or object storage (e.g. S3).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
