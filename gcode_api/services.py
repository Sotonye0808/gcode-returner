"""
Service layer for GCode API business logic.

This module contains the core business logic for SVG to G-code conversion
and evaluation metrics. It acts as an interface between the API views
and the underlying conversion/evaluation modules.

The service layer provides:
- SVG to G-code conversion functionality
- SSIM calculation for image comparison
- Line smoothness analysis
- G-code execution error calculation
- File handling and temporary file management
- Error handling and logging

Classes:
    SVGConversionService: Handles SVG to G-code conversion
    EvaluationService: Handles all evaluation metrics
"""

import os
import tempfile
import logging
from typing import Tuple, Optional, List, Union, Dict, Any
import base64
import io
import numpy as np
import cv2
from PIL import Image
import hmac
import hashlib
import json
from datetime import datetime
from django.conf import settings
from django.utils import timezone

# Import our existing modules
from py_svg2gcode import SVGConverter
from evaluation_modules.ssim import compute_ssim
from evaluation_modules.line_smoothness import smoothness_test
from evaluation_modules.gcode_error import execution_error
from .models import User, SignatureData

logger = logging.getLogger(__name__)


class SVGConversionService:
    """
    Service class for handling SVG to G-code conversion.
    
    This service provides a clean interface for converting SVG data
    to G-code using the existing py_svg2gcode module.
    """
    
    @staticmethod
    def convert_svg_to_gcode(svg_content: str) -> str:
        """
        Convert SVG content to G-code.
        
        Args:
            svg_content (str): The SVG content as a string
            
        Returns:
            str: Generated G-code content
            
        Raises:
            ValueError: If SVG content is invalid
            RuntimeError: If conversion fails
        """
        try:
            # Create a temporary file for the SVG content
            with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as temp_file:
                temp_file.write(svg_content)
                temp_svg_path = temp_file.name
            
            try:
                # Create converter and generate G-code
                converter = SVGConverter(debugging=False, toDefDir=False)
                gcode = converter.generate_gcode(temp_svg_path)
                
                if not gcode or not gcode.strip():
                    raise ValueError("Generated G-code is empty")
                
                logger.info(f"Successfully converted SVG to G-code ({len(gcode)} characters)")
                return gcode
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_svg_path):
                    os.unlink(temp_svg_path)
                    
        except Exception as e:
            logger.error(f"Error converting SVG to G-code: {str(e)}")
            raise RuntimeError(f"SVG conversion failed: {str(e)}")


class EvaluationService:
    """
    Service class for handling evaluation metrics.
    
    This service provides methods for calculating various evaluation
    metrics for signature analysis and G-code execution quality.
    """
    
    @staticmethod
    def _prepare_image_from_file(image_file) -> str:
        """
        Save uploaded file to temporary location.
        
        Args:
            image_file: Django uploaded file object
            
        Returns:
            str: Path to temporary file
        """
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        try:
            for chunk in image_file.chunks():
                temp_file.write(chunk)
            temp_file.flush()
            return temp_file.name
        finally:
            temp_file.close()
    
    @staticmethod
    def _prepare_image_from_base64(base64_data: str) -> str:
        """
        Convert base64 image data to temporary file.
        
        Args:
            base64_data (str): Base64 encoded image data
            
        Returns:
            str: Path to temporary file
        """
        try:
            # Remove data URL prefix if present
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]
            
            # Decode base64 data
            image_data = base64.b64decode(base64_data)
            
            # Convert to PIL Image and save as temporary file
            image = Image.open(io.BytesIO(image_data))
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            image.save(temp_file.name, 'PNG')
            temp_file.close()
            
            return temp_file.name
            
        except Exception as e:
            raise ValueError(f"Invalid base64 image data: {str(e)}")
    
    @staticmethod
    def calculate_ssim(
        original_image=None, 
        reproduced_image=None,
        original_image_data=None,
        reproduced_image_data=None
    ) -> float:
        """
        Calculate SSIM between two images.
        
        Args:
            original_image: Original image file (Django UploadedFile)
            reproduced_image: Reproduced image file (Django UploadedFile)
            original_image_data (str): Base64 encoded original image
            reproduced_image_data (str): Base64 encoded reproduced image
            
        Returns:
            float: SSIM score between 0 and 1
            
        Raises:
            ValueError: If image processing fails
        """
        temp_files = []
        try:
            # Prepare image paths
            if original_image and reproduced_image:
                original_path = EvaluationService._prepare_image_from_file(original_image)
                reproduced_path = EvaluationService._prepare_image_from_file(reproduced_image)
            else:
                original_path = EvaluationService._prepare_image_from_base64(original_image_data) # type: ignore
                reproduced_path = EvaluationService._prepare_image_from_base64(reproduced_image_data) # type: ignore
            
            temp_files.extend([original_path, reproduced_path])
            
            # Calculate SSIM using existing module
            ssim_score = compute_ssim(original_path=original_path, reproduced_path=reproduced_path)
            
            if ssim_score is None:
                raise ValueError("SSIM calculation failed")
            
            logger.info(f"SSIM calculated successfully: {ssim_score:.4f}")
            return float(ssim_score)
            
        except Exception as e:
            logger.error(f"Error calculating SSIM: {str(e)}")
            raise ValueError(f"SSIM calculation failed: {str(e)}")
        finally:
            # Clean up temporary files
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
    
    @staticmethod
    def calculate_smoothness(image=None, image_data=None) -> float:
        """
        Calculate line smoothness score for an image.
        
        Args:
            image: Image file (Django UploadedFile)
            image_data (str): Base64 encoded image data
            
        Returns:
            float: Smoothness score between 0 and 1
            
        Raises:
            ValueError: If image processing fails
        """
        temp_file = None
        try:
            # Prepare image path
            if image:
                temp_file = EvaluationService._prepare_image_from_file(image)
            else:
                temp_file = EvaluationService._prepare_image_from_base64(image_data) # type: ignore
            
            # Calculate smoothness using existing module
            smoothness_score = smoothness_test(temp_file)
            
            logger.info(f"Smoothness calculated successfully: {smoothness_score:.4f}")
            return float(smoothness_score)
            
        except Exception as e:
            logger.error(f"Error calculating smoothness: {str(e)}")
            raise ValueError(f"Smoothness calculation failed: {str(e)}")
        finally:
            # Clean up temporary file
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)
    
    @staticmethod
    def calculate_execution_error(
        expected_toolpath: List[List[float]], 
        actual_toolpath: List[List[float]]
    ) -> Tuple[float, List[float]]:
        """
        Calculate G-code execution error between expected and actual toolpaths.
        
        Args:
            expected_toolpath: List of [x, y] coordinate pairs for expected path
            actual_toolpath: List of [x, y] coordinate pairs for actual path
            
        Returns:
            tuple: (mean_error, individual_errors)
                - mean_error (float): Average execution error
                - individual_errors (List[float]): Error at each point
                
        Raises:
            ValueError: If calculation fails
        """
        try:
            # Convert to numpy arrays
            expected = np.array(expected_toolpath)
            actual = np.array(actual_toolpath)
            
            # Calculate execution error using existing module
            mean_error, errors = execution_error(expected, actual)
            
            if mean_error is None:
                raise ValueError("Execution error calculation failed")
            
            logger.info(f"Execution error calculated successfully: {mean_error:.4f}")
            return float(mean_error), errors.tolist() # type: ignore
            
        except Exception as e:
            logger.error(f"Error calculating execution error: {str(e)}")
            raise ValueError(f"Execution error calculation failed: {str(e)}")


class SignatureVerificationService:
    """
    Service for verifying signed requests from trusted frontend origins.
    
    This service handles HMAC signature verification to ensure requests
    are coming from authorized frontend applications.
    """
    
    @staticmethod
    def get_trusted_origins():
        """Get list of trusted frontend origins."""
        # Get from environment variable or use defaults
        trusted_origins = os.environ.get('TRUSTED_FRONTEND_ORIGINS', '')
        if trusted_origins:
            return [origin.strip() for origin in trusted_origins.split(',') if origin.strip()]
        
        # Fallback to defaults (for development)
        if settings.DEBUG:
            return [
                'http://localhost:3000',
                'http://127.0.0.1:3000',
                'http://localhost:4200',
                'http://127.0.0.1:4200',
            ]
        else:
            # Production defaults
            return [
                'https://signature-eu.web.app',
            ]
    
    @staticmethod
    def get_signing_key():
        """Get the signing key for HMAC verification."""
        # In production, this should come from environment variables
        key = getattr(settings, 'FRONTEND_SIGNING_KEY', 'dev-signing-key-change-in-production')
        # Strip any extra quotes or whitespace
        return key.strip().strip('"').strip("'")
    
    @staticmethod
    def verify_request_signature(data: Dict[str, Any], signature: str, origin: str) -> bool:
        """
        Verify HMAC signature for a request.
        
        Args:
            data: Request data to verify
            signature: HMAC signature to verify
            origin: Request origin
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        try:
            # Check if origin is trusted
            trusted_origins = SignatureVerificationService.get_trusted_origins()
            """ logger.info(f"Request origin: {origin}")
            logger.info(f"Trusted origins: {trusted_origins}") """
            
            if origin not in trusted_origins:
                logger.warning(f"Request from untrusted origin: {origin}")
                return False
            
            # Create canonical string from data
            canonical_data = SignatureVerificationService._create_canonical_string(data)
            #logger.info(f"Backend canonical string: {canonical_data}")
            
            # Calculate expected signature
            signing_key = SignatureVerificationService.get_signing_key()
            #logger.info(f"Backend signing key(len={len(signing_key)}): '{signing_key}'")
            
            expected_signature = hmac.new(
                signing_key.encode('utf-8'),
                canonical_data.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            """ logger.info(f"Expected signature: {expected_signature}")
            logger.info(f"Received signature: {signature}")
            logger.info(f"Signature lengths - Expected: {len(expected_signature)}, Received: {len(signature)}") """
            
            # Compare signatures
            is_valid = hmac.compare_digest(signature, expected_signature)
            #logger.info(f"Signature valid: {is_valid}")
            
            return is_valid
        
        except Exception as e:
            logger.error(f"Error verifying request signature: {str(e)}")
            return False
    
    @staticmethod
    def _create_canonical_string(data: Dict[str, Any]) -> str:
        """
        Create canonical string representation of data for signing.
        
        Args:
            data: Dictionary of data to canonicalize
            
        Returns:
            str: Canonical string representation
        """
        # Remove signature field from data
        clean_data = {k: v for k, v in data.items() if k != 'request_signature'}
        #logger.info(f"Backend clean data: {clean_data}")
        
        # Sort keys and create canonical string
        sorted_items = sorted(clean_data.items())
        #logger.info(f"Backend sorted items: {sorted_items}")

        canonical_parts = []
        
        for key, value in sorted_items:
            #logger.info(f"Processing key '{key}' with value '{value}' (type: {type(value)})")

            if isinstance(value, dict):
                value = json.dumps(value, sort_keys=True)
                #logger.info(f"  -> dict converted to: '{value}'")
            elif isinstance(value, list):
                value = json.dumps(value, sort_keys=True)
                #logger.info(f"  -> list converted to: '{value}'")
            elif value is None:
                value = ''
                #logger.info(f"  -> None converted to: '{value}'")
            else:
                value = str(value)
                #logger.info(f"  -> converted to string: '{value}'")
        
            part = f"{key}={value}"
            canonical_parts.append(part)
            #logger.info(f"  -> canonical part: '{part}'")
        
        canonical_string = "&".join(canonical_parts)
        """ 
        logger.info(f"Backend canonical string: '{canonical_string}'")
        logger.info(f"Backend canonical length: {len(canonical_string)}") """
        
        return canonical_string


class UserDataService:
    """
    Service for managing user data in the playground database.
    
    This service handles user creation, updates, and data retrieval
    for the testing and data collection phase.
    """
    
    @staticmethod
    def create_or_update_user(user_data: Dict[str, Any]) -> User:
        """
        Create a new user or update existing user based on email.
        
        Args:
            user_data: Dictionary containing user information
            
        Returns:
            User: Created or updated user instance
        """
        try:
            email = user_data['email'].lower()
            
            # Try to get existing user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'name': user_data['name'],
                    'role': user_data.get('role', 'student'),
                    'department': user_data.get('department', ''),
                    'faculty': user_data.get('faculty', ''),
                    'submitted_at': user_data.get('submitted_at', timezone.now())
                }
            )
            
            # Update existing user if not created
            if not created:
                user.name = user_data['name']
                user.role = user_data.get('role', user.role)
                user.department = user_data.get('department', user.department)
                user.faculty = user_data.get('faculty', user.faculty)
                # Don't update submitted_at for existing users
                user.save()
                
                logger.info(f"Updated existing user: {email}")
            else:
                logger.info(f"Created new user: {email}")
            
            return user
            
        except Exception as e:
            logger.error(f"Error creating/updating user: {str(e)}")
            raise ValueError(f"Failed to create/update user: {str(e)}")
    
    @staticmethod
    def store_signature_data(user: User, svg_data: str) -> SignatureData:
        """
        Store signature SVG data and generate G-code for a user.
        
        Args:
            user: User instance
            svg_data: SVG content
            
        Returns:
            SignatureData: Created signature data instance
        """
        try:
            # Generate G-code from SVG
            gcode = SVGConversionService.convert_svg_to_gcode(svg_data)
            
            # Calculate metadata
            gcode_lines_list = [line.strip() for line in gcode.split('\n') if line.strip()]
            gcode_lines = len(gcode_lines_list)
            gcode_size = len(gcode.encode('utf-8'))
            
            movement_commands = len([line for line in gcode_lines_list if line.startswith(('G0', 'G1', 'G2', 'G3'))])
            setup_commands = len([line for line in gcode_lines_list if line.startswith(('G28', 'G90', 'G91', 'M'))])
            
            metadata = {
                'gcode_lines': gcode_lines,
                'gcode_size': gcode_size,
                'movement_commands': movement_commands,
                'setup_commands': setup_commands,
                'estimated_duration': f"{gcode_lines * 0.1:.1f} seconds"
            }
            
            # Create signature data record
            signature_data = SignatureData.objects.create(
                user=user,
                svg_data=svg_data,
                gcode_data=gcode,
                gcode_metadata=metadata
            )
            
            logger.info(f"Stored signature data for user: {user.email}")
            return signature_data
            
        except Exception as e:
            logger.error(f"Error storing signature data: {str(e)}")
            raise ValueError(f"Failed to store signature data: {str(e)}")
    
    @staticmethod
    def get_user_data(email: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve all data for a user by email.
        
        Args:
            email: User's email address
            
        Returns:
            dict: User data with signatures, or None if not found
        """
        try:
            email = email.lower()
            user = User.objects.get(email=email)
            
            # Get all signatures for the user
            signatures = SignatureData.objects.filter(user=user).order_by('-created_at')
            
            user_data = {
                'user': {
                    'id': user.id, # type: ignore
                    'name': user.name,
                    'email': user.email,
                    'role': user.role,
                    'department': user.department,
                    'faculty': user.faculty,
                    'created_at': user.created_at.isoformat(),
                    'updated_at': user.updated_at.isoformat(),
                    'submitted_at': user.submitted_at.isoformat()
                },
                'signatures': []
            }
            
            for signature in signatures:
                signature_info = {
                    'id': signature.id, # type: ignore
                    'svg_data': signature.svg_data,
                    'gcode_data': signature.gcode_data,
                    'metadata': signature.gcode_metadata,
                    'created_at': signature.created_at.isoformat()
                }
                user_data['signatures'].append(signature_info)
            
            logger.info(f"Retrieved data for user: {email}")
            return user_data
            
        except User.DoesNotExist:
            logger.info(f"User not found: {email}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving user data: {str(e)}")
            raise ValueError(f"Failed to retrieve user data: {str(e)}")
