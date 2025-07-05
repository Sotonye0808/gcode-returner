"""
Django app configuration for GCode API.

This module defines the configuration for the gcode_api Django app.
It sets the app name and default auto field type.
"""

from django.apps import AppConfig


class GcodeApiConfig(AppConfig):
    """
    Configuration class for the GCode API app.
    
    This class configures the app settings including the default auto field
    type and the app name used throughout the Django project.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gcode_api'
    verbose_name = 'GCode API'
