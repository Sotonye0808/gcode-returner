"""
Django models for the GCode API.

This module contains Django model definitions for the gcode_api app.
Currently, the API is stateless and doesn't require persistent storage
for core functionality, but this file can be extended to include models
for logging, user management, or caching if needed in the future.

Potential future models:
- ConversionLog: Track SVG to G-code conversions
- EvaluationLog: Track evaluation metric calculations
- UserProfile: User management and API usage tracking
- FileCache: Cache converted files for performance
"""

from django.db import models

# Currently no models are needed for the stateless API
# This file is kept for future extensibility
