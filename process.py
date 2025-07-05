# To be deprecated or refactored to main.py using OOP principles. Mostly due to discovery of open-source integratable signature pad that can save in PNG, JPG and most importantly, SVG
# method for processing signature images can still be used to convert image of expected signature to cleaner form to compare the signature pad output to the expected signature

import cv2
import os
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
common_dir = os.getenv("COMMON_DIR")

def process_signature(image_path, output_path_png):
    try:
        # Read image
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError("Could not read image")

        # Normalize size while preserving aspect ratio
        max_dim = 800
        height, width = img.shape
        scale = max_dim / max(width, height)
        img = cv2.resize(img, None, fx=scale, fy=scale)

        # Enhanced preprocessing
        blur = cv2.GaussianBlur(img, (3, 3), 0)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(blur)

        # Adaptive thresholding with reduced noise
        thresh = cv2.adaptiveThreshold(
            enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )

        # Connected component analysis
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh)
        
        # Filter components based on size and proximity
        min_size = 20
        max_distance = 30
        mask = np.zeros_like(thresh)
        
        for i in range(1, num_labels):
            if stats[i, cv2.CC_STAT_AREA] > min_size:
                mask[labels == i] = 255
                
                # Connect nearby components
                x, y = centroids[i]
                for j in range(1, num_labels):
                    if i != j and stats[j, cv2.CC_STAT_AREA] > min_size:
                        x2, y2 = centroids[j]
                        distance = np.sqrt((x2-x)**2 + (y2-y)**2)
                        if distance < max_distance:
                            cv2.line(mask, 
                                   (int(x), int(y)), 
                                   (int(x2), int(y2)), 
                                   255, 1)

        # Enhance details
        kernel = np.ones((2,2), np.uint8)
        result = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Save processed PNG
        cv2.imwrite(output_path_png, result)
        
        return output_path_png

    except Exception as e:
        print(f"Error: {str(e)}")
        return None, None
    
    
if __name__ == "__main__":
    shared_dir = f"{dir}/testing_images"
    input_path = f"{shared_dir}/signature.jpg"
    output_png = f"{shared_dir}/signature.png"
    png_path, svg_path = process_signature(input_path, output_png)
    if png_path:
        print(f"Processed signature saved as:\nPNG: {png_path}")