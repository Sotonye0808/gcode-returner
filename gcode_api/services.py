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
from typing import Tuple, Optional, List, Union
import base64
import io
import numpy as np
import cv2
from PIL import Image

# Import our existing modules
from py_svg2gcode import SVGConverter
from evaluation_modules.ssim import compute_ssim
from evaluation_modules.line_smoothness import smoothness_test
from evaluation_modules.gcode_error import execution_error

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
