"""
Django admin configuration for the GCode API.

This module configures the Django admin interface for the gcode_api app.
Currently, the API doesn't have models that require admin management,
but this file can be extended to include admin configurations for
future models such as logging, user management, or caching.

The admin interface can be useful for:
- Monitoring API usage and performance
- Managing user access and permissions
- Viewing conversion and evaluation logs
- Managing cached files and cleanup
"""

from django.contrib import admin

# Currently no models to register
# This file is kept for future extensibility when models are added
