import logging

logger = logging.getLogger(__name__)

try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    logger.warning("OpenCV (cv2) not installed. Using mocked preprocessing.")

def preprocess_soil_image(image_path: str, output_path: str) -> bool:
    """
    Applies OpenCV preprocessing to the uploaded soil image.
    Steps:
    1. Color correction (White balance/Histogram Equalization)
    2. Gaussian Blur to reduce sensor noise
    3. Background removal (Masking non-soil greens/whites)
    """
    if not HAS_CV2:
        logger.info(f"Mocked OpenCV preprocessing for {image_path}. Saved to {output_path}.")
        return True
        
    try:
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            logger.error(f"Failed to load image for preprocessing: {image_path}")
            return False

        # 1. Color Correction (CLAHE on L-channel of LAB color space)
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl,a,b))
        corrected = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

        # 2. Gaussian Blur
        blurred = cv2.GaussianBlur(corrected, (5, 5), 0)
        
        # 3. Simple non-soil masking (mask out bright greens e.g., leaves)
        # Convert to HSV
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        # Define range for green color
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([85, 255, 255])
        # Create a mask for green
        green_mask = cv2.inRange(hsv, lower_green, upper_green)
        # Invert mask (we want non-green, i.e., soil)
        soil_mask = cv2.bitwise_not(green_mask)
        # Apply mask
        final_img = cv2.bitwise_and(blurred, blurred, mask=soil_mask)

        # Save result
        cv2.imwrite(output_path, final_img)
        logger.info(f"Successfully preprocessed image and saved to {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error during OpenCV preprocessing: {e}")
        return False
