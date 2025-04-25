import cv2
import numpy as np
from skimage import filters
from PIL import Image, ImageTk

class CartoonFilter:
    """
    A class that provides various methods to transform images into cartoon-like renditions.
    """
    
    def __init__(self):
        """Initialize with default parameters"""
        # Edge detection parameters
        self.edge_detection_method = "canny"  # Options: canny, sobel, laplacian
        self.canny_threshold1 = 100
        self.canny_threshold2 = 200
        self.sobel_kernel_size = 3
        self.edge_blur = 5
        
        # Bilateral filter parameters
        self.bilateral_d = 9
        self.bilateral_sigma_color = 75
        self.bilateral_sigma_space = 75
        
        # Color quantization parameters
        self.quantization_method = "kmeans"  # Options: kmeans, uniform
        self.num_colors = 8
        
        # Extra parameters
        self.line_size = 7
        self.blur_strength = 7
        self.edge_preserve = True
        self.saturation_factor = 1.5
        
    def detect_edges(self, img):
        """
        Detect edges in the image using selected method
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply gaussian blur to reduce noise
        if self.edge_blur > 0:
            gray = cv2.GaussianBlur(gray, (self.edge_blur, self.edge_blur), 0)
            
        if self.edge_detection_method == "canny":
            edges = cv2.Canny(gray, self.canny_threshold1, self.canny_threshold2)
        elif self.edge_detection_method == "sobel":
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=self.sobel_kernel_size)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=self.sobel_kernel_size)
            edges = cv2.magnitude(sobelx, sobely)
            # Normalize to 0-255
            edges = cv2.normalize(edges, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
            # Apply threshold
            _, edges = cv2.threshold(edges, self.canny_threshold1, 255, cv2.THRESH_BINARY)
        elif self.edge_detection_method == "laplacian":
            edges = cv2.Laplacian(gray, cv2.CV_64F)
            edges = cv2.convertScaleAbs(edges)
            _, edges = cv2.threshold(edges, self.canny_threshold1, 255, cv2.THRESH_BINARY)
        
        # Dilate edges for thicker lines if needed
        if self.line_size > 1:
            kernel = np.ones((self.line_size, self.line_size), np.uint8)
            edges = cv2.dilate(edges, kernel, iterations=1)
        
        return edges

    def apply_bilateral_filter(self, img):
        """
        Apply bilateral filter for edge-preserving smoothing
        """
        if self.edge_preserve:
            # Apply multiple times for stronger effect
            filtered = img
            for _ in range(2):  # Apply twice for better smoothing
                filtered = cv2.bilateralFilter(
                    filtered, 
                    self.bilateral_d, 
                    self.bilateral_sigma_color, 
                    self.bilateral_sigma_space
                )
            return filtered
        else:
            # If edge preservation is not needed, use median blur
            return cv2.medianBlur(img, self.blur_strength)

    def quantize_colors(self, img):
        """
        Reduce the number of colors in the image
        """
        if self.quantization_method == "kmeans":
            # Reshape the image
            data = img.reshape((-1, 3))
            data = np.float32(data)
            
            # Define criteria and apply kmeans
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
            _, labels, centers = cv2.kmeans(
                data, 
                self.num_colors, 
                None, 
                criteria, 
                10, 
                cv2.KMEANS_RANDOM_CENTERS
            )
            
            # Convert back to uint8 and reshape back to the original image
            centers = np.uint8(centers)
            result = centers[labels.flatten()]
            result = result.reshape(img.shape)
            return result
        
        elif self.quantization_method == "uniform":
            # Apply uniform quantization - simpler but less effective
            div = 256 // self.num_colors
            result = img // div * div
            return result

    def enhance_saturation(self, img):
        """
        Enhance the color saturation of the image
        """
        # Convert to HSV
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # Scale the saturation channel
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * self.saturation_factor, 0, 255).astype(np.uint8)
        # Convert back to BGR
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    def apply_cartoon_effect(self, img):
        """
        Apply the cartoon effect to the image
        """
        # 1. Apply bilateral filter for edge-preserving smoothing
        filtered = self.apply_bilateral_filter(img)
        
        # 2. Detect edges
        edges = self.detect_edges(img)
        
        # 3. Color quantization for cartoon-like appearance
        quantized = self.quantize_colors(filtered)
        
        # 4. Enhance color saturation
        saturated = self.enhance_saturation(quantized)
        
        # 5. Merge edges with color image
        edges_inv = cv2.bitwise_not(edges)
        edges_inv = cv2.cvtColor(edges_inv, cv2.COLOR_GRAY2BGR)
        
        # Blend edges with the color image
        result = cv2.bitwise_and(saturated, edges_inv)
        
        return {
            'cartoon': result,
            'edges': edges,
            'filtered': filtered,
            'quantized': quantized
        }

    def get_cv2_image_for_tk(self, img, size=None):
        """
        Convert an OpenCV image to a format suitable for Tkinter
        """
        if size:
            img = cv2.resize(img, size)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_img)
        return ImageTk.PhotoImage(pil_img)
        
    def resize_image(self, img, max_width=800, max_height=600):
        """
        Resize image while maintaining aspect ratio
        """
        height, width = img.shape[:2]
        
        # Calculate the ratio of the width and height to the max size
        width_ratio = max_width / width
        height_ratio = max_height / height
        
        # Take the smallest ratio to ensure it fits within the max dimensions
        ratio = min(width_ratio, height_ratio)
        
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        
        return cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA) 