"""
URL configuration for the GCode API app.

This module defines the URL patterns for all API endpoints in the gcode_api app.
It provides a RESTful API structure for SVG to G-code conversion and evaluation.

API Endpoints:
- POST /api/convert/ - Convert SVG data to G-code
- POST /api/evaluate/ssim/ - Calculate SSIM between two images
- POST /api/evaluate/smoothness/ - Calculate line smoothness score
- POST /api/evaluate/execution-error/ - Calculate G-code execution error
- GET /api/health/ - Health check endpoint

All endpoints return JSON responses and support proper HTTP status codes.
Detailed API documentation is available at each endpoint.

Example usage:
    POST /api/convert/
    Content-Type: application/json
    {
        "svg_data": "<svg>...</svg>"
    }
    
    Response:
    {
        "success": true,
        "gcode": "G28\\nG1 Z0.0\\n...",
        "message": "SVG converted successfully"
    }
"""

from django.urls import path
from . import views

app_name = 'gcode_api'

urlpatterns = [
    # Main conversion endpoint
    path('convert/', views.SVGToGCodeView.as_view(), name='svg_to_gcode'),
    
    # Evaluation endpoints
    path('evaluate/ssim/', views.SSIMEvaluationView.as_view(), name='ssim_evaluation'),
    path('evaluate/smoothness/', views.SmoothnessEvaluationView.as_view(), name='smoothness_evaluation'),
    path('evaluate/execution-error/', views.ExecutionErrorView.as_view(), name='execution_error'),
    
    # Health check endpoint
    path('health/', views.HealthCheckView.as_view(), name='health_check'),
]
