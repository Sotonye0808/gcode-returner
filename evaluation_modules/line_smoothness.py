import numpy as np
import cv2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
common_dir = os.getenv("COMMON_DIR")

def smoothness_test(image_path):
    try:
        # Input validation
        if not os.path.exists(image_path):
            raise FileNotFoundError("Image file not found")
            
        # Load and preprocess image
        signature = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if signature is None:
            raise ValueError("Could not read image")
            
        # Apply Gaussian blur to reduce noise
        signature = cv2.GaussianBlur(signature, (3,3), 0)
        
        # Edge detection with optimized parameters
        edges = cv2.Canny(signature, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        curvature_variances = []

        for contour in contours:
            contour = contour.squeeze()
            if len(contour.shape) < 2 or len(contour) < 3:
                continue
                
            # Calculate gradients
            dx = np.gradient(contour[:, 0].astype(float))
            dy = np.gradient(contour[:, 1].astype(float))
            ddx = np.gradient(dx)
            ddy = np.gradient(dy)
            
            # Avoid division by zero with small epsilon
            denominator = (dx**2 + dy**2)**1.5
            epsilon = 1e-10
            denominator = np.where(denominator < epsilon, epsilon, denominator)
            
            # Calculate curvature safely
            curvature = np.abs(ddx * dy - dx * ddy) / denominator
            
            # Filter out invalid values
            valid_curvature = curvature[~np.isnan(curvature)]
            if len(valid_curvature) > 0:
                curvature_variances.append(np.var(valid_curvature))

        # Compute normalized smoothness score
        if curvature_variances:
            smoothness_score = 1.0 / (1.0 + np.mean(curvature_variances))
        else:
            smoothness_score = 0.0
            
        return smoothness_score

    except Exception as e:
        print(f"Error processing signature: {str(e)}")
        return 0.0

if __name__ == "__main__":
    input_path = f"{dir}/testing_images/signature.jpg"
    score = smoothness_test(input_path)
    print(f"Line Smoothness Score: {score:.4f}")