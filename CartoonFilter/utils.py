import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

def load_image(file_path):
    """
    Load an image from file using OpenCV
    
    Args:
        file_path (str): Path to the image file
        
    Returns:
        numpy.ndarray: Loaded image in BGR format or None if loading failed
    """
    if not os.path.exists(file_path):
        return None
    
    try:
        img = cv2.imread(file_path)
        return img
    except Exception:
        return None

def save_image(img, file_path):
    """
    Save an image to a file
    
    Args:
        img (numpy.ndarray): Image to save
        file_path (str): Path where to save the image
        
    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        cv2.imwrite(file_path, img)
        return True
    except Exception:
        return False

def create_comparison_grid(images, titles=None, figsize=(12, 8)):
    """
    Create a comparison grid of images
    
    Args:
        images (list): List of images to display
        titles (list): List of titles for each image
        figsize (tuple): Figure size
        
    Returns:
        matplotlib.figure.Figure: Figure with the comparison grid
    """
    n = len(images)
    if n <= 0:
        return None
    
    # Determine grid dimensions
    if n <= 3:
        rows, cols = 1, n
    elif n <= 6:
        rows, cols = 2, 3
    elif n <= 9:
        rows, cols = 3, 3
    else:
        rows = (n + 3) // 4  # Ceiling division
        cols = 4
    
    # Create figure
    fig, axes = plt.subplots(rows, cols, figsize=figsize)
    
    # Convert to flat array for easier indexing
    if n > 1:
        axes = axes.flatten()
    else:
        axes = [axes]
    
    # Plot each image
    for i in range(n):
        if i < len(images):
            img = images[i]
            
            # Convert BGR to RGB if necessary
            if len(img.shape) == 3 and img.shape[2] == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            axes[i].imshow(img)
            axes[i].axis('off')
            
            if titles and i < len(titles):
                axes[i].set_title(titles[i])
    
    # Hide unused subplots
    for i in range(n, len(axes)):
        axes[i].axis('off')
    
    plt.tight_layout()
    return fig

def get_file_size_str(file_path):
    """
    Get the file size as a formatted string
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: Formatted file size (B, KB, MB)
    """
    if not os.path.exists(file_path):
        return "N/A"
    
    size_bytes = os.path.getsize(file_path)
    
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

def get_image_dimensions(img):
    """
    Get image dimensions
    
    Args:
        img (numpy.ndarray): Image
        
    Returns:
        tuple: (width, height)
    """
    if img is None:
        return (0, 0)
    
    height, width = img.shape[:2]
    return (width, height)

def resize_keep_aspect_ratio(img, target_width=None, target_height=None):
    """
    Resize image keeping aspect ratio
    
    Args:
        img (numpy.ndarray): Image to resize
        target_width (int): Target width
        target_height (int): Target height
        
    Returns:
        numpy.ndarray: Resized image
    """
    if img is None:
        return None
    
    height, width = img.shape[:2]
    
    # If both dimensions are specified, use the smaller scale
    if target_width and target_height:
        scale_width = target_width / width
        scale_height = target_height / height
        scale = min(scale_width, scale_height)
        new_width = int(width * scale)
        new_height = int(height * scale)
    
    # If only width is specified
    elif target_width:
        scale = target_width / width
        new_width = target_width
        new_height = int(height * scale)
    
    # If only height is specified
    elif target_height:
        scale = target_height / height
        new_width = int(width * scale)
        new_height = target_height
    
    # If no target dimensions specified, return original
    else:
        return img
    
    return cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)

def pil_to_cv2(pil_image):
    """
    Convert PIL Image to OpenCV format
    
    Args:
        pil_image (PIL.Image): PIL Image
        
    Returns:
        numpy.ndarray: OpenCV image (BGR)
    """
    if pil_image is None:
        return None
    
    # Convert PIL Image to RGB numpy array
    rgb_image = np.array(pil_image)
    
    # Convert RGB to BGR (OpenCV format)
    bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
    
    return bgr_image

def cv2_to_pil(cv2_image):
    """
    Convert OpenCV image to PIL Image
    
    Args:
        cv2_image (numpy.ndarray): OpenCV image (BGR)
        
    Returns:
        PIL.Image: PIL Image
    """
    if cv2_image is None:
        return None
    
    # Convert BGR to RGB
    rgb_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
    
    # Convert to PIL Image
    return Image.fromarray(rgb_image)

def add_text_overlay(img, text, position=(20, 40), font_scale=1.0, color=(255, 255, 255), thickness=2):
    """
    Add text overlay to an image
    
    Args:
        img (numpy.ndarray): Image
        text (str): Text to add
        position (tuple): Position (x, y)
        font_scale (float): Font scale
        color (tuple): Text color (BGR)
        thickness (int): Text thickness
        
    Returns:
        numpy.ndarray: Image with text overlay
    """
    result = img.copy()
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # Add black outline for better visibility
    cv2.putText(result, text, position, font, font_scale, (0, 0, 0), thickness + 2)
    
    # Add main text
    cv2.putText(result, text, position, font, font_scale, color, thickness)
    
    return result 