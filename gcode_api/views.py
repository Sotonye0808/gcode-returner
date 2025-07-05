"""
API views for the GCode API.

This module contains Django REST Framework views that handle HTTP requests
for SVG to G-code conversion and evaluation endpoints.

The views provide:
- RESTful API endpoints with proper HTTP methods
- Comprehensive error handling and validation
- Detailed API documentation
- Consistent JSON response formats
- Request/response logging

Classes:
    SVGToGCodeView: Handles SVG to G-code conversion requests
    SSIMEvaluationView: Handles SSIM calculation requests
    SmoothnessEvaluationView: Handles line smoothness evaluation requests
    ExecutionErrorView: Handles G-code execution error calculation requests
    HealthCheckView: Provides API health status
"""

import logging
import numpy as np
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.http import JsonResponse

from .serializers import (
    SVGToGCodeSerializer,
    SSIMEvaluationSerializer,
    SmoothnessEvaluationSerializer,
    ExecutionErrorSerializer
)
from .services import SVGConversionService, EvaluationService

logger = logging.getLogger(__name__)


class SVGToGCodeView(APIView):
    """
    API view for converting SVG data to G-code.
    
    This endpoint accepts SVG content either as a file upload or as raw SVG data
    and returns the equivalent G-code for CNC/3D printer execution.
    
    **Endpoint:** `POST /api/convert/`
    
    **Request Methods:** POST
    
    **Request Format:**
    - Content-Type: application/json OR multipart/form-data
    - Body (JSON): {"svg_data": "<svg>...</svg>"}
    - Body (Form): svg_file=<file.svg>
    
    **Response Format:**
    ```json
    {
        "success": true,
        "gcode": "G28\\nG1 Z0.0\\nM05\\n...",
        "message": "SVG converted successfully to G-code",
        "metadata": {
            "gcode_lines": 150,
            "gcode_size": 2048
        }
    }
    ```
    
    **Error Response:**
    ```json
    {
        "success": false,
        "error": "Error message",
        "details": "Detailed error information"
    }
    ```
    
    **Status Codes:**
    - 200: Conversion successful
    - 400: Bad request (invalid SVG data)
    - 500: Internal server error
    """
    
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def post(self, request, *args, **kwargs):
        """
        Handle POST request for SVG to G-code conversion.
        
        Args:
            request: HTTP request object containing SVG data
            
        Returns:
            Response: JSON response with G-code or error message
        """
        try:
            # Validate input data
            serializer = SVGToGCodeSerializer(data=request.data)
            if not serializer.is_valid():
                logger.warning(f"Invalid SVG conversion request: {serializer.errors}")
                return Response({
                    'success': False,
                    'error': 'Invalid input data',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Extract SVG content
            validated_data = serializer.validated_data
            svg_content = ""
            
            if validated_data.get('svg_file'):
                svg_content = validated_data['svg_file'].read().decode('utf-8')
                logger.info(f"Processing SVG file: {validated_data['svg_file'].name}")
            else:
                svg_content = validated_data['svg_data']
                logger.info("Processing SVG data from request body")
            
            # Convert SVG to G-code
            gcode = SVGConversionService.convert_svg_to_gcode(svg_content)
            
            # Calculate metadata
            gcode_lines = len(gcode.split('\\n'))
            gcode_size = len(gcode.encode('utf-8'))
            
            logger.info(f"SVG conversion successful: {gcode_lines} lines, {gcode_size} bytes")
            
            return Response({
                'success': True,
                'gcode': gcode,
                'message': 'SVG converted successfully to G-code',
                'metadata': {
                    'gcode_lines': gcode_lines,
                    'gcode_size': gcode_size
                }
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            logger.error(f"SVG conversion validation error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Invalid SVG data',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"SVG conversion server error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Internal server error',
                'details': 'An unexpected error occurred during conversion'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SSIMEvaluationView(APIView):
    """
    API view for calculating SSIM (Structural Similarity Index) between two images.
    
    This endpoint compares two images and returns a similarity score between 0 and 1,
    where 1 indicates identical images and 0 indicates completely different images.
    
    **Endpoint:** `POST /api/evaluate/ssim/`
    
    **Request Methods:** POST
    
    **Request Format:**
    - Content-Type: multipart/form-data OR application/json
    - Form: original_image=<file>, reproduced_image=<file>
    - JSON: {"original_image_data": "base64...", "reproduced_image_data": "base64..."}
    
    **Response Format:**
    ```json
    {
        "success": true,
        "ssim_score": 0.8542,
        "similarity_percentage": 85.42,
        "message": "SSIM calculated successfully"
    }
    ```
    
    **Status Codes:**
    - 200: Calculation successful
    - 400: Bad request (invalid image data)
    - 500: Internal server error
    """
    
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def post(self, request, *args, **kwargs):
        """Handle POST request for SSIM calculation."""
        try:
            serializer = SSIMEvaluationSerializer(data=request.data)
            if not serializer.is_valid():
                logger.warning(f"Invalid SSIM request: {serializer.errors}")
                return Response({
                    'success': False,
                    'error': 'Invalid input data',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            validated_data = serializer.validated_data
            
            # Calculate SSIM
            ssim_score = EvaluationService.calculate_ssim(
                original_image=validated_data.get('original_image'),
                reproduced_image=validated_data.get('reproduced_image'),
                original_image_data=validated_data.get('original_image_data'),
                reproduced_image_data=validated_data.get('reproduced_image_data')
            )
            
            logger.info(f"SSIM calculation successful: {ssim_score:.4f}")
            
            return Response({
                'success': True,
                'ssim_score': round(ssim_score, 4),
                'similarity_percentage': round(ssim_score * 100, 2),
                'message': 'SSIM calculated successfully'
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            logger.error(f"SSIM calculation validation error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Invalid image data',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"SSIM calculation server error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Internal server error',
                'details': 'An unexpected error occurred during SSIM calculation'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SmoothnessEvaluationView(APIView):
    """
    API view for calculating line smoothness score of an image.
    
    This endpoint analyzes an image to determine how smooth and consistent
    the lines are, returning a score between 0 and 1 where higher values
    indicate smoother lines.
    
    **Endpoint:** `POST /api/evaluate/smoothness/`
    
    **Request Methods:** POST
    
    **Request Format:**
    - Content-Type: multipart/form-data OR application/json
    - Form: image=<file>
    - JSON: {"image_data": "base64..."}
    
    **Response Format:**
    ```json
    {
        "success": true,
        "smoothness_score": 0.7823,
        "smoothness_percentage": 78.23,
        "quality_rating": "Good",
        "message": "Line smoothness calculated successfully"
    }
    ```
    
    **Status Codes:**
    - 200: Calculation successful
    - 400: Bad request (invalid image data)
    - 500: Internal server error
    """
    
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def post(self, request, *args, **kwargs):
        """Handle POST request for smoothness calculation."""
        try:
            serializer = SmoothnessEvaluationSerializer(data=request.data)
            if not serializer.is_valid():
                logger.warning(f"Invalid smoothness request: {serializer.errors}")
                return Response({
                    'success': False,
                    'error': 'Invalid input data',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            validated_data = serializer.validated_data
            
            # Calculate smoothness
            smoothness_score = EvaluationService.calculate_smoothness(
                image=validated_data.get('image'),
                image_data=validated_data.get('image_data')
            )
            
            # Determine quality rating
            if smoothness_score >= 0.8:
                quality_rating = "Excellent"
            elif smoothness_score >= 0.6:
                quality_rating = "Good"
            elif smoothness_score >= 0.4:
                quality_rating = "Fair"
            else:
                quality_rating = "Poor"
            
            logger.info(f"Smoothness calculation successful: {smoothness_score:.4f}")
            
            return Response({
                'success': True,
                'smoothness_score': round(smoothness_score, 4),
                'smoothness_percentage': round(smoothness_score * 100, 2),
                'quality_rating': quality_rating,
                'message': 'Line smoothness calculated successfully'
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            logger.error(f"Smoothness calculation validation error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Invalid image data',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Smoothness calculation server error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Internal server error',
                'details': 'An unexpected error occurred during smoothness calculation'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExecutionErrorView(APIView):
    """
    API view for calculating G-code execution error.
    
    This endpoint compares expected vs actual toolpath coordinates to determine
    how accurately a CNC machine or robot followed the G-code instructions.
    
    **Endpoint:** `POST /api/evaluate/execution-error/`
    
    **Request Methods:** POST
    
    **Request Format:**
    ```json
    {
        "expected_toolpath": [[10, 20], [15, 25], [20, 30]],
        "actual_toolpath": [[10, 21], [14, 26], [19, 31]]
    }
    ```
    
    **Response Format:**
    ```json
    {
        "success": true,
        "mean_error": 1.247,
        "individual_errors": [1.0, 1.414, 1.414],
        "max_error": 1.414,
        "min_error": 1.0,
        "error_std": 0.239,
        "accuracy_percentage": 87.53,
        "message": "Execution error calculated successfully"
    }
    ```
    
    **Status Codes:**
    - 200: Calculation successful
    - 400: Bad request (invalid toolpath data)
    - 500: Internal server error
    """
    
    parser_classes = [JSONParser]
    
    def post(self, request, *args, **kwargs):
        """Handle POST request for execution error calculation."""
        try:
            serializer = ExecutionErrorSerializer(data=request.data)
            if not serializer.is_valid():
                logger.warning(f"Invalid execution error request: {serializer.errors}")
                return Response({
                    'success': False,
                    'error': 'Invalid input data',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            validated_data = serializer.validated_data
            
            # Calculate execution error
            mean_error, individual_errors = EvaluationService.calculate_execution_error(
                expected_toolpath=validated_data['expected_toolpath'],
                actual_toolpath=validated_data['actual_toolpath']
            )
            
            # Calculate additional statistics
            max_error = max(individual_errors)
            min_error = min(individual_errors)
            error_std = np.std(individual_errors)
            
            # Calculate accuracy percentage (inverse of normalized error)
            # Assuming maximum reasonable error is 10 units for normalization
            max_reasonable_error = 10.0
            accuracy_percentage = max(0, (1 - min(mean_error / max_reasonable_error, 1)) * 100)
            
            logger.info(f"Execution error calculation successful: {mean_error:.4f}")
            
            return Response({
                'success': True,
                'mean_error': round(mean_error, 4),
                'individual_errors': [round(e, 4) for e in individual_errors],
                'max_error': round(max_error, 4),
                'min_error': round(min_error, 4),
                'error_std': round(error_std, 4),
                'accuracy_percentage': round(accuracy_percentage, 2),
                'message': 'Execution error calculated successfully'
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            logger.error(f"Execution error validation error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Invalid toolpath data',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Execution error server error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Internal server error',
                'details': 'An unexpected error occurred during execution error calculation'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HealthCheckView(APIView):
    """
    API view for health check endpoint.
    
    This endpoint provides a simple health check for the API service,
    returning service status and version information.
    
    **Endpoint:** `GET /api/health/`
    
    **Request Methods:** GET
    
    **Response Format:**
    ```json
    {
        "status": "healthy",
        "service": "GCode Returner API",
        "version": "1.0.0",
        "timestamp": "2024-01-01T12:00:00Z",
        "endpoints": {
            "convert": "/api/convert/",
            "ssim": "/api/evaluate/ssim/",
            "smoothness": "/api/evaluate/smoothness/",
            "execution_error": "/api/evaluate/execution-error/"
        }
    }
    ```
    
    **Status Codes:**
    - 200: Service is healthy
    """
    
    def get(self, request, *args, **kwargs):
        """Handle GET request for health check."""
        from django.utils import timezone
        
        return Response({
            'status': 'healthy',
            'service': 'GCode Returner API',
            'version': '1.0.0',
            'timestamp': timezone.now().isoformat(),
            'endpoints': {
                'convert': '/api/convert/',
                'ssim': '/api/evaluate/ssim/',
                'smoothness': '/api/evaluate/smoothness/',
                'execution_error': '/api/evaluate/execution-error/'
            }
        }, status=status.HTTP_200_OK)
