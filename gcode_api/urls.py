"""
URL configuration for the GCode API app.

This module defines the URL patterns for all API endpoints in the gcode_api app.
It provides a RESTful API structure for SVG to G-code conversion, evaluation,
and signed data storage/retrieval for trusted frontend origins.

API Endpoints:
- POST /api/convert/ - Convert SVG data to G-code (open access)
- POST /api/evaluate/ssim/ - Calculate SSIM between two images (open access)
- POST /api/evaluate/smoothness/ - Calculate line smoothness score (open access)
- POST /api/evaluate/execution-error/ - Calculate G-code execution error (open access)
- GET /api/health/ - Health check endpoint (open access)

Signed Endpoints (require HMAC signature from trusted origins):
- POST /api/signed/submit/ - Submit user data and signature for storage
- POST /api/signed/retrieve/ - Retrieve user data by email

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
    # Main conversion endpoint (open access)
    path('convert/', views.SVGToGCodeView.as_view(), name='svg_to_gcode'),
    
    # Evaluation endpoints (open access)
    path('evaluate/ssim/', views.SSIMEvaluationView.as_view(), name='ssim_evaluation'),
    path('evaluate/smoothness/', views.SmoothnessEvaluationView.as_view(), name='smoothness_evaluation'),
    path('evaluate/execution-error/', views.ExecutionErrorView.as_view(), name='execution_error'),
    
    # Health check endpoint (open access)
    path('health/', views.HealthCheckView.as_view(), name='health_check'),
    
    # Signed endpoints (require HMAC signature from trusted origins)
    path('signed/submit/', views.SignedSubmissionView.as_view(), name='signed_submission'),
    path('signed/retrieve/', views.UserDataRetrievalView.as_view(), name='user_data_retrieval'),
]
