"""
Serializers for the GCode API.

This module contains Django REST Framework serializers that handle
data validation and serialization for all API endpoints.

The serializers provide:
- Input validation for API requests
- Data transformation and cleaning
- Error handling for invalid data
- Documentation for API request/response formats

Classes:
    SVGToGCodeSerializer: Handles SVG data input for conversion
    SSIMEvaluationSerializer: Handles image comparison inputs
    SmoothnessEvaluationSerializer: Handles image smoothness analysis input
    ExecutionErrorSerializer: Handles toolpath comparison inputs
"""

from rest_framework import serializers
from django.core.files.uploadedfile import InMemoryUploadedFile
from .models import User, SignatureData
import base64
import io
from PIL import Image
import numpy as np


class SVGToGCodeSerializer(serializers.Serializer):
    """
    Serializer for SVG to G-code conversion endpoint.
    
    Accepts either SVG file upload or raw SVG data string.
    Validates SVG format and content before processing.
    
    Fields:
        svg_file (FileField, optional): SVG file upload
        svg_data (CharField, optional): Raw SVG content as string
        
    Validation:
        - At least one of svg_file or svg_data must be provided
        - SVG content must be valid XML
        - File must have .svg extension if uploaded
    """
    svg_file = serializers.FileField(required=False, help_text="SVG file to convert")
    svg_data = serializers.CharField(required=False, help_text="Raw SVG content as string")
    
    def validate(self, data):
        """Validate that either svg_file or svg_data is provided."""
        if not data.get('svg_file') and not data.get('svg_data'):
            raise serializers.ValidationError(
                "Either 'svg_file' or 'svg_data' must be provided."
            )
        
        # Validate file extension if svg_file is provided
        if data.get('svg_file'):
            file = data['svg_file']
            if not file.name.lower().endswith('.svg'):
                raise serializers.ValidationError(
                    "File must have .svg extension."
                )
        
        # Basic SVG validation
        # Basic SVG validation - only validate raw SVG data, not file uploads
        if data.get('svg_data'):
            svg_content = data['svg_data']
            if not svg_content.strip().startswith('<svg'):
                raise serializers.ValidationError(
                    "Invalid SVG content. Must start with <svg tag."
                )
        
        # For file uploads, we'll validate the content in the view after reading
        # This avoids file pointer issues during validation
            
        return data


class SSIMEvaluationSerializer(serializers.Serializer):
    """
    Serializer for SSIM (Structural Similarity Index) evaluation endpoint.
    
    Accepts two images for comparison either as file uploads or base64 encoded data.
    Validates image formats and ensures both images are provided.
    
    Fields:
        original_image (FileField, optional): Original image file
        reproduced_image (FileField, optional): Reproduced image file
        original_image_data (CharField, optional): Base64 encoded original image
        reproduced_image_data (CharField, optional): Base64 encoded reproduced image
        
    Validation:
        - Both original and reproduced images must be provided
        - Images must be in supported formats (PNG, JPG, JPEG)
        - Base64 data must be valid if provided
    """
    original_image = serializers.FileField(required=False, help_text="Original image file")
    reproduced_image = serializers.FileField(required=False, help_text="Reproduced image file")
    original_image_data = serializers.CharField(required=False, help_text="Base64 encoded original image")
    reproduced_image_data = serializers.CharField(required=False, help_text="Base64 encoded reproduced image")
    
    def validate(self, data):
        """Validate that both images are provided in some form."""
        has_files = data.get('original_image') and data.get('reproduced_image')
        has_data = data.get('original_image_data') and data.get('reproduced_image_data')
        
        if not has_files and not has_data:
            raise serializers.ValidationError(
                "Both original and reproduced images must be provided either as files or base64 data."
            )
            
        # Validate file extensions if files are provided
        if has_files:
            valid_extensions = ['.png', '.jpg', '.jpeg']
            for field_name in ['original_image', 'reproduced_image']:
                file = data[field_name]
                if not any(file.name.lower().endswith(ext) for ext in valid_extensions):
                    raise serializers.ValidationError(
                        f"{field_name} must be a PNG or JPEG file."
                    )
        
        # Validate base64 data if provided
        if has_data:
            try:
                for field_name in ['original_image_data', 'reproduced_image_data']:
                    base64_data = data[field_name]
                    # Remove data URL prefix if present
                    if ',' in base64_data:
                        base64_data = base64_data.split(',')[1]
                    base64.b64decode(base64_data)
            except Exception:
                raise serializers.ValidationError(
                    "Invalid base64 image data provided."
                )
                
        return data


class SmoothnessEvaluationSerializer(serializers.Serializer):
    """
    Serializer for line smoothness evaluation endpoint.
    
    Accepts a single image for smoothness analysis either as file upload or base64 data.
    
    Fields:
        image (FileField, optional): Image file to analyze
        image_data (CharField, optional): Base64 encoded image data
        
    Validation:
        - One of image or image_data must be provided
        - Image must be in supported format
        - Base64 data must be valid if provided
    """
    image = serializers.FileField(required=False, help_text="Image file to analyze for smoothness")
    image_data = serializers.CharField(required=False, help_text="Base64 encoded image data")
    
    def validate(self, data):
        """Validate that an image is provided."""
        if not data.get('image') and not data.get('image_data'):
            raise serializers.ValidationError(
                "Either 'image' or 'image_data' must be provided."
            )
            
        # Validate file extension if file is provided
        if data.get('image'):
            file = data['image']
            valid_extensions = ['.png', '.jpg', '.jpeg']
            if not any(file.name.lower().endswith(ext) for ext in valid_extensions):
                raise serializers.ValidationError(
                    "Image must be a PNG or JPEG file."
                )
        
        # Validate base64 data if provided
        if data.get('image_data'):
            try:
                base64_data = data['image_data']
                # Remove data URL prefix if present
                if ',' in base64_data:
                    base64_data = base64_data.split(',')[1]
                base64.b64decode(base64_data)
            except Exception:
                raise serializers.ValidationError(
                    "Invalid base64 image data provided."
                )
                
        return data


class ExecutionErrorSerializer(serializers.Serializer):
    """
    Serializer for G-code execution error evaluation endpoint.
    
    Accepts expected and actual toolpath data for comparison analysis.
    
    Fields:
        expected_toolpath (ListField): Expected toolpath coordinates
        actual_toolpath (ListField): Actual executed toolpath coordinates
        
    Validation:
        - Both toolpaths must be provided
        - Toolpaths must be arrays of [x, y] coordinate pairs
        - Coordinate arrays must have the same length
        - All coordinates must be numeric
    """
    expected_toolpath = serializers.ListField(
        child=serializers.ListField(
            child=serializers.FloatField(),
            min_length=2,
            max_length=2
        ),
        help_text="Expected toolpath as array of [x, y] coordinates"
    )
    actual_toolpath = serializers.ListField(
        child=serializers.ListField(
            child=serializers.FloatField(),
            min_length=2,
            max_length=2
        ),
        help_text="Actual toolpath as array of [x, y] coordinates"
    )
    
    def validate(self, data):
        """Validate that toolpaths have matching dimensions."""
        expected = data.get('expected_toolpath', [])
        actual = data.get('actual_toolpath', [])
        
        if len(expected) != len(actual):
            raise serializers.ValidationError(
                "Expected and actual toolpaths must have the same number of points."
            )
            
        if len(expected) == 0:
            raise serializers.ValidationError(
                "Toolpaths cannot be empty."
            )
            
        return data


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    
    Handles user data validation and serialization for the playground database.
    """
    
    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'role', 'department', 
            'faculty', 'created_at', 'updated_at', 'submitted_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_email(self, value):
        """Validate email format."""
        if not value or '@' not in value:
            raise serializers.ValidationError("Valid email address is required.")
        return value.lower()


class SignatureDataSerializer(serializers.ModelSerializer):
    """
    Serializer for SignatureData model.
    
    Handles signature SVG and G-code data serialization.
    """
    
    user_email = serializers.EmailField(write_only=True, required=False)
    user_name = serializers.CharField(source='user.name', read_only=True)
    gcode_lines = serializers.SerializerMethodField()
    gcode_size = serializers.SerializerMethodField()
    
    class Meta:
        model = SignatureData
        fields = [
            'id', 'user_email', 'user_name', 'svg_data', 'gcode_data',
            'gcode_metadata', 'gcode_lines', 'gcode_size', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'gcode_lines', 'gcode_size']
    
    def get_gcode_lines(self, obj):
        """Get G-code lines from metadata."""
        return obj.get_gcode_lines()
    
    def get_gcode_size(self, obj):
        """Get G-code size from metadata."""
        return obj.get_gcode_size()


class SignedSubmissionSerializer(serializers.Serializer):
    """
    Serializer for signed submission requests from frontend.
    
    Handles user data and signature submission with signature verification.
    """
    
    # User data
    name = serializers.CharField(max_length=255, help_text="User's full name")
    email = serializers.EmailField(help_text="User's email address")
    role = serializers.ChoiceField(
        choices=User.ROLE_CHOICES,
        default='student',
        help_text="User's role"
    )
    department = serializers.CharField(
        max_length=255, 
        required=False, 
        allow_blank=True,
        help_text="User's department"
    )
    faculty = serializers.CharField(
        max_length=255, 
        required=False, 
        allow_blank=True,
        help_text="User's faculty"
    )
    submitted_at = serializers.DateTimeField(
        required=False,
        help_text="Submission timestamp"
    )
    
    # Signature data
    svg_data = serializers.CharField(help_text="SVG signature data")
    
    # Request signature for verification
    request_signature = serializers.CharField(
        help_text="HMAC signature for request verification"
    )
    
    def validate_email(self, value):
        """Validate and normalize email."""
        return value.lower().strip()
    
    def validate_svg_data(self, value):
        """Validate SVG data format."""
        if not value or not value.strip():
            raise serializers.ValidationError("SVG data cannot be empty.")
        
        if not value.strip().startswith('<svg'):
            raise serializers.ValidationError("Invalid SVG format.")
        
        return value
    
    def validate(self, data):
        """Additional validation for the entire request."""
        # Ensure required fields are present
        required_fields = ['name', 'email', 'svg_data', 'request_signature']
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError(f"{field} is required.")
        
        return data


class UserDataRetrievalSerializer(serializers.Serializer):
    """
    Serializer for user data retrieval requests.
    
    Handles email-based data retrieval with signature verification.
    """
    
    email = serializers.EmailField(help_text="User's email address")
    request_signature = serializers.CharField(
        help_text="HMAC signature for request verification"
    )
    
    def validate_email(self, value):
        """Validate and normalize email."""
        return value.lower().strip()
