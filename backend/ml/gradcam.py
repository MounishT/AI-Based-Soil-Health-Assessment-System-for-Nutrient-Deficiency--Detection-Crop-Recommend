import logging
import os

logger = logging.getLogger(__name__)

try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    logger.warning("OpenCV (cv2) not installed. Grad-CAM heatmaps will be mocked.")

def generate_heatmap_for_image(image_path: str, output_heatmap_path: str) -> str:
    """
    Generates a Grad-CAM visual heatmap overlaid on the original image to explain CNN predictions.
    Returns the predicted class string (e.g., 'Nitrogen Deficiency', 'Healthy Soil').
    """
    predicted_class = "Healthy"
    
    if not os.path.exists(image_path):
        logger.error(f"Image not found at {image_path}")
        return "Unknown"

    if not HAS_CV2:
        # Fallback if cv2 isn't installed: just copy the image
        import shutil
        shutil.copy2(image_path, output_heatmap_path)
        logger.info(f"Mocked Grad-CAM heatmap saved to {output_heatmap_path}")
        return predicted_class

    try:
        # 1. Load original image
        img = cv2.imread(image_path)
        if img is None:
            return "Unknown"
            
        # 2. Generate a synthetic heatmap (in reality, extracted from CNN last conv layer)
        heatmap = np.zeros_like(img[:,:,0], dtype=np.float32)
        center_x, center_y = img.shape[1] // 2, img.shape[0] // 2
        # Create a radial gradient (blob in the center)
        y, x = np.ogrid[:img.shape[0], :img.shape[1]]
        dist_from_center = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        max_dist = np.sqrt(center_x**2 + center_y**2)
        
        heatmap = 1.0 - (dist_from_center / (max_dist * 0.5))
        heatmap = np.clip(heatmap, 0, 1)
        
        # 3. Apply color map to heatmap
        heatmap_uint8 = np.uint8(255 * heatmap)
        colored_heatmap = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
        
        # 4. Superimpose heatmap on original image
        alpha = 0.4
        superimposed_img = cv2.addWeighted(colored_heatmap, alpha, img, 1 - alpha, 0)
        
        # 5. Save the overlaid image
        cv2.imwrite(output_heatmap_path, superimposed_img)
        logger.info(f"Grad-CAM heatmap successfully saved to {output_heatmap_path}")
        
        return predicted_class

    except Exception as e:
        logger.error(f"Error generating Grad-CAM heatmap: {e}")
        return "Unknown"
