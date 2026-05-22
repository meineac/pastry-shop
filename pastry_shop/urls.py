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

# Media file serving

urlpatterns += [
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
]
