#!/usr/bin/env python3
import os
import sys
import tkinter as tk
from app import CartoonApp
import utils

def setup_sample_images():
    """
    Sets up sample images directory if it doesn't exist
    Returns True if the directory exists or was created
    """
    # Create sample images directory if it doesn't exist
    sample_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
    if not os.path.exists(sample_dir):
        try:
            os.makedirs(sample_dir)
            print(f"Created sample images directory: {sample_dir}")
            print("Please add some sample images to this directory.")
            return True
        except Exception as e:
            print(f"Error creating sample directory: {e}")
            return False
    return True

def check_dependencies():
    """
    Check if all required dependencies are installed
    Returns True if all dependencies are available
    """
    try:
        import cv2
        import numpy
        import PIL
        import matplotlib
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install all required dependencies using:")
        print("pip install -r requirements.txt")
        return False

def main():
    """Main entry point for the Cartoon Filter application"""
    print("Starting Advanced Cartoon Filter...")
    
    # Check if dependencies are installed
    if not check_dependencies():
        print("Error: Missing dependencies")
        sys.exit(1)
    
    # Setup sample images directory
    setup_sample_images()
    
    # Create and start the Tkinter application
    root = tk.Tk()
    app = CartoonApp(root)
    
    # Set app icon if available
    try:
        # Try to set application icon
        if os.path.exists("CartoonFilter/images/app_icon.png"):
            icon = tk.PhotoImage(file="CartoonFilter/images/app_icon.png")
            root.iconphoto(True, icon)
    except Exception:
        pass
    
    # Start the main event loop
    root.mainloop()

if __name__ == "__main__":
    main() 