"""
Test Script for GCode Returner API

This script provides basic functionality testing for the Django API endpoints.
It can be used to verify that the API is working correctly after setup.

Usage:
    python test_api.py

Requirements:
    - Django server must be running on localhost:8000
    - requests library must be installed (pip install requests)
"""

import requests
import json
import base64
import os

# API base URL
BASE_URL = "http://localhost:8000/api"

def test_health_check():
    """Test the health check endpoint."""
    print("Testing health check endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health/")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health check passed: {data['status']}")
            print(f"  Service: {data['service']}")
            print(f"  Version: {data['version']}")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health check error: {str(e)}")
        return False

def test_svg_conversion():
    """Test SVG to G-code conversion endpoint."""
    print("\nTesting SVG to G-code conversion...")
    
    # Simple SVG data
    svg_data = '''<?xml version="1.0" encoding="UTF-8"?>
    <svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
        <rect x="10" y="10" width="80" height="80" fill="none" stroke="black" stroke-width="2"/>
    </svg>'''
    
    try:
        response = requests.post(
            f"{BASE_URL}/convert/",
            json={"svg_data": svg_data},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✓ SVG conversion successful")
                print(f"  G-code lines: {data['metadata']['gcode_lines']}")
                print(f"  G-code size: {data['metadata']['gcode_size']} bytes")
                return True
            else:
                print(f"✗ SVG conversion failed: {data.get('error')}")
                return False
        else:
            print(f"✗ SVG conversion failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ SVG conversion error: {str(e)}")
        return False

def test_execution_error():
    """Test G-code execution error endpoint."""
    print("\nTesting execution error calculation...")
    
    test_data = {
        "expected_toolpath": [
            [10.0, 20.0],
            [15.0, 25.0],
            [20.0, 30.0],
            [25.0, 35.0]
        ],
        "actual_toolpath": [
            [10.0, 21.0],
            [14.0, 26.0],
            [19.0, 31.0],
            [26.0, 34.0]
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/evaluate/execution-error/",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✓ Execution error calculation successful")
                print(f"  Mean error: {data['mean_error']}")
                print(f"  Accuracy: {data['accuracy_percentage']}%")
                return True
            else:
                print(f"✗ Execution error calculation failed: {data.get('error')}")
                return False
        else:
            print(f"✗ Execution error calculation failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Execution error calculation error: {str(e)}")
        return False

def create_test_image():
    """Create a simple test image for testing image endpoints."""
    try:
        from PIL import Image, ImageDraw
        
        # Create a simple test image
        img = Image.new('RGB', (200, 100), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw a simple signature-like curve
        points = [(20, 50), (50, 30), (100, 40), (150, 60), (180, 50)]
        for i in range(len(points) - 1):
            draw.line([points[i], points[i + 1]], fill='black', width=3)
        
        # Save as temporary file
        temp_path = "temp_test_image.png"
        img.save(temp_path)
        return temp_path
    except ImportError:
        print("  PIL not available, skipping image tests")
        return None
    except Exception as e:
        print(f"  Error creating test image: {str(e)}")
        return None

def test_smoothness_evaluation():
    """Test line smoothness evaluation endpoint."""
    print("\nTesting line smoothness evaluation...")
    
    # Create test image
    test_image_path = create_test_image()
    if not test_image_path:
        print("✗ Could not create test image")
        return False
    
    try:
        # Convert image to base64
        with open(test_image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode()
        
        response = requests.post(
            f"{BASE_URL}/evaluate/smoothness/",
            json={"image_data": f"data:image/png;base64,{image_data}"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✓ Smoothness evaluation successful")
                print(f"  Smoothness score: {data['smoothness_score']}")
                print(f"  Quality rating: {data['quality_rating']}")
                return True
            else:
                print(f"✗ Smoothness evaluation failed: {data.get('error')}")
                return False
        else:
            print(f"✗ Smoothness evaluation failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Smoothness evaluation error: {str(e)}")
        return False
    finally:
        # Clean up test image
        if os.path.exists(test_image_path):
            os.remove(test_image_path)

def main():
    """Run all API tests."""
    print("GCode Returner API Test Suite")
    print("=" * 40)
    
    tests = [
        test_health_check,
        test_svg_conversion,
        test_execution_error,
        test_smoothness_evaluation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! API is working correctly.")
    else:
        print("✗ Some tests failed. Please check the API server and configuration.")
        print("\nTroubleshooting tips:")
        print("1. Make sure the Django server is running: python manage.py runserver")
        print("2. Check that all dependencies are installed: pip install -r requirements.txt")
        print("3. Verify the .env file is configured correctly")
        print("4. Check the server logs for any error messages")

if __name__ == "__main__":
    main()
