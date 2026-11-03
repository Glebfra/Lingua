"""
URL configuration for lingua project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/languages/", include("lingua_languages.urls")),
    path("api/v1/dictionary/", include("lingua_dictionary.urls")),
    path("api/v1/learning/", include("lingua_learning.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
