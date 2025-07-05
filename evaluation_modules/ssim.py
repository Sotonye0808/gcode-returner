import cv2
import os
from skimage.metrics import structural_similarity as ssim
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
common_dir = os.getenv("COMMON_DIR")

def compute_ssim(original_path=None, reproduced_path=None, original_image=None, reproduced_image=None):
    try:
        # Load images 
        # if paths are provided
        if original_path and reproduced_path:
            original = cv2.imread(original_path, cv2.IMREAD_GRAYSCALE)
            reproduced = cv2.imread(reproduced_path, cv2.IMREAD_GRAYSCALE)
        # if actual images are provided, format to png/Matlike
        elif original_image is not None and reproduced_image is not None:
            original = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
            reproduced = cv2.cvtColor(reproduced_image, cv2.COLOR_BGR2GRAY)
        else:
            raise ValueError("Either image paths or image arrays must be provided")

        # Resize to match dimensions
        reproduced = cv2.resize(reproduced, (original.shape[1], original.shape[0]))

        # Compute SSIM
        score, _ = ssim(original, reproduced, full=True)
        return score

    except Exception as e:
        print(f"Error processing signature: {str(e)}")

"""
SSIM = 1 → Perfect match
SSIM close to 1 → High similarity
SSIM close to 0 → Low similarity
"""

# Experimental usage
if __name__ == "__main__":
    shared_dir = f"{dir}/testing_images"
    orig_path = f"{shared_dir}/signature.jpg"
    rep_path = f"{shared_dir}/signature.png"
    # using paths
    result = compute_ssim(orig_path, rep_path)
    print(f"SSIM Score: {result:.4f}")
    # if to use images
    """ original_image = cv2.imread(input_path)
    reproduced_image = cv2.imread(output_path)
    compute_ssim(original_image=original_image, reproduced_image=reproduced_image) """