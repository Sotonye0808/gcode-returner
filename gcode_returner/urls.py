"""
Main URL configuration for the GCode Returner API.

This module defines the root URL patterns for the Django backend API.
It includes routes for the main API endpoints and admin interface.

The API provides the following main endpoints:
- /api/convert/ - SVG to G-code conversion
- /api/evaluate/ - Signature evaluation endpoints
- /admin/ - Django admin interface

For more information on URL patterns, see:
https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('gcode_api.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
