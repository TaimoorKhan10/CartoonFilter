import os
import cv2
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from cartoon_filter import CartoonFilter
import threading
import time
from preset_loader import PresetLoader, create_preset_from_filter

class CartoonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Cartoon Filter")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Initialize the cartoon filter
        self.cartoon_filter = CartoonFilter()
        
        # Initialize variables
        self.preset_loader = PresetLoader()
        self.current_image = None
        self.original_image = None
        self.cartoon_result = None
        self.processing_thread = None
        self.is_processing = False
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create the UI
        self.create_ui()
        
        # Bind window resize event
        self.root.bind("<Configure>", self.on_window_resize)
        
    def create_ui(self):
        # Split the main frame into left (controls) and right (image display)
        self.left_frame = ttk.Frame(self.main_frame, width=300)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create controls
        self.create_control_panel()
        
        # Create image display area
        self.create_display_area()
        
        # Create status bar
        self.create_status_bar()
        
    def create_control_panel(self):
        # Main controls frame with scrollbar
        control_canvas = tk.Canvas(self.left_frame, width=280)
        scrollbar = ttk.Scrollbar(self.left_frame, orient="vertical", command=control_canvas.yview)
        self.scrollable_frame = ttk.Frame(control_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: control_canvas.configure(scrollregion=control_canvas.bbox("all"))
        )
        
        control_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        control_canvas.configure(yscrollcommand=scrollbar.set)
        
        control_canvas.pack(side="left", fill="y", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # File operations
        file_frame = ttk.LabelFrame(self.scrollable_frame, text="File Operations", padding=(10, 5))
        file_frame.pack(fill=tk.X, pady=5)
        
        load_btn = ttk.Button(file_frame, text="Load Image", command=self.load_image)
        load_btn.pack(fill=tk.X, pady=2)
        
        save_btn = ttk.Button(file_frame, text="Save Cartoon", command=self.save_cartoon)
        save_btn.pack(fill=tk.X, pady=2)
        
        batch_btn = ttk.Button(file_frame, text="Batch Process", command=self.batch_process)
        batch_btn.pack(fill=tk.X, pady=2)
        
        # Edge detection parameters
        edge_frame = ttk.LabelFrame(self.scrollable_frame, text="Edge Detection", padding=(10, 5))
        edge_frame.pack(fill=tk.X, pady=5)
        
        # Edge detection method
        ttk.Label(edge_frame, text="Method:").pack(anchor=tk.W)
        self.edge_method_var = tk.StringVar(value=self.cartoon_filter.edge_detection_method)
        edge_methods = ttk.Combobox(edge_frame, textvariable=self.edge_method_var, 
                                   values=["canny", "sobel", "laplacian"])
        edge_methods.pack(fill=tk.X, pady=2)
        edge_methods.bind("<<ComboboxSelected>>", self.update_preview)
        
        # Canny threshold 1
        ttk.Label(edge_frame, text="Threshold 1:").pack(anchor=tk.W)
        self.threshold1_var = tk.IntVar(value=self.cartoon_filter.canny_threshold1)
        threshold1_scale = ttk.Scale(
            edge_frame, from_=0, to=255, variable=self.threshold1_var,
            command=lambda _: self.update_preview()
        )
        threshold1_scale.pack(fill=tk.X, pady=2)
        
        # Canny threshold 2
        ttk.Label(edge_frame, text="Threshold 2:").pack(anchor=tk.W)
        self.threshold2_var = tk.IntVar(value=self.cartoon_filter.canny_threshold2)
        threshold2_scale = ttk.Scale(
            edge_frame, from_=0, to=255, variable=self.threshold2_var,
            command=lambda _: self.update_preview()
        )
        threshold2_scale.pack(fill=tk.X, pady=2)
        
        # Edge blur
        ttk.Label(edge_frame, text="Edge Blur:").pack(anchor=tk.W)
        self.edge_blur_var = tk.IntVar(value=self.cartoon_filter.edge_blur)
        edge_blur_scale = ttk.Scale(
            edge_frame, from_=0, to=15, variable=self.edge_blur_var,
            command=lambda _: self.update_preview()
        )
        edge_blur_scale.pack(fill=tk.X, pady=2)
        
        # Line size
        ttk.Label(edge_frame, text="Line Size:").pack(anchor=tk.W)
        self.line_size_var = tk.IntVar(value=self.cartoon_filter.line_size)
        line_size_scale = ttk.Scale(
            edge_frame, from_=1, to=15, variable=self.line_size_var,
            command=lambda _: self.update_preview()
        )
        line_size_scale.pack(fill=tk.X, pady=2)
        
        # Bilateral filter parameters
        bilateral_frame = ttk.LabelFrame(self.scrollable_frame, text="Bilateral Filter", padding=(10, 5))
        bilateral_frame.pack(fill=tk.X, pady=5)
        
        # Edge preserve checkbox
        self.edge_preserve_var = tk.BooleanVar(value=self.cartoon_filter.edge_preserve)
        edge_preserve_cb = ttk.Checkbutton(
            bilateral_frame, text="Edge Preservation", 
            variable=self.edge_preserve_var, 
            command=self.update_preview
        )
        edge_preserve_cb.pack(anchor=tk.W, pady=2)
        
        # Bilateral d
        ttk.Label(bilateral_frame, text="Filter Diameter:").pack(anchor=tk.W)
        self.bilateral_d_var = tk.IntVar(value=self.cartoon_filter.bilateral_d)
        bilateral_d_scale = ttk.Scale(
            bilateral_frame, from_=1, to=25, variable=self.bilateral_d_var,
            command=lambda _: self.update_preview()
        )
        bilateral_d_scale.pack(fill=tk.X, pady=2)
        
        # Bilateral sigma color
        ttk.Label(bilateral_frame, text="Sigma Color:").pack(anchor=tk.W)
        self.bilateral_sigma_color_var = tk.IntVar(value=self.cartoon_filter.bilateral_sigma_color)
        bilateral_sigma_color_scale = ttk.Scale(
            bilateral_frame, from_=10, to=250, variable=self.bilateral_sigma_color_var,
            command=lambda _: self.update_preview()
        )
        bilateral_sigma_color_scale.pack(fill=tk.X, pady=2)
        
        # Bilateral sigma space
        ttk.Label(bilateral_frame, text="Sigma Space:").pack(anchor=tk.W)
        self.bilateral_sigma_space_var = tk.IntVar(value=self.cartoon_filter.bilateral_sigma_space)
        bilateral_sigma_space_scale = ttk.Scale(
            bilateral_frame, from_=10, to=250, variable=self.bilateral_sigma_space_var,
            command=lambda _: self.update_preview()
        )
        bilateral_sigma_space_scale.pack(fill=tk.X, pady=2)
        
        # Color quantization parameters
        color_frame = ttk.LabelFrame(self.scrollable_frame, text="Color Quantization", padding=(10, 5))
        color_frame.pack(fill=tk.X, pady=5)
        
        # Quantization method
        ttk.Label(color_frame, text="Method:").pack(anchor=tk.W)
        self.quant_method_var = tk.StringVar(value=self.cartoon_filter.quantization_method)
        quant_methods = ttk.Combobox(
            color_frame, textvariable=self.quant_method_var, 
            values=["kmeans", "uniform"]
        )
        quant_methods.pack(fill=tk.X, pady=2)
        quant_methods.bind("<<ComboboxSelected>>", self.update_preview)
        
        # Number of colors
        ttk.Label(color_frame, text="Number of Colors:").pack(anchor=tk.W)
        self.num_colors_var = tk.IntVar(value=self.cartoon_filter.num_colors)
        num_colors_scale = ttk.Scale(
            color_frame, from_=2, to=32, variable=self.num_colors_var,
            command=lambda _: self.update_preview()
        )
        num_colors_scale.pack(fill=tk.X, pady=2)
        
        # Saturation factor
        ttk.Label(color_frame, text="Saturation:").pack(anchor=tk.W)
        self.saturation_var = tk.DoubleVar(value=self.cartoon_filter.saturation_factor)
        saturation_scale = ttk.Scale(
            color_frame, from_=0.5, to=3.0, variable=self.saturation_var,
            command=lambda _: self.update_preview()
        )
        saturation_scale.pack(fill=tk.X, pady=2)
        
        # Presets frame
        presets_frame = ttk.LabelFrame(self.scrollable_frame, text="Style Presets", padding=(10, 5))
        presets_frame.pack(fill=tk.X, pady=5)
        
        # Preset selection
        ttk.Label(presets_frame, text="Select Preset:").pack(anchor=tk.W)
        self.preset_var = tk.StringVar()
        self.preset_combo = ttk.Combobox(presets_frame, textvariable=self.preset_var, 
                                        values=self.preset_loader.get_preset_names())
        self.preset_combo.pack(fill=tk.X, pady=2)
        self.preset_combo.bind("<<ComboboxSelected>>", self.apply_preset)
        
        # Preset buttons frame
        preset_btn_frame = ttk.Frame(presets_frame)
        preset_btn_frame.pack(fill=tk.X, pady=5)
        
        # Load preset button
        load_preset_btn = ttk.Button(preset_btn_frame, text="Apply Preset", 
                                     command=lambda: self.apply_preset(None))
        load_preset_btn.pack(side=tk.LEFT, padx=2)
        
        # Save preset button
        save_preset_btn = ttk.Button(preset_btn_frame, text="Save Current", 
                                     command=self.save_current_preset)
        save_preset_btn.pack(side=tk.RIGHT, padx=2)
        
        # Apply button
        apply_frame = ttk.Frame(self.scrollable_frame)
        apply_frame.pack(fill=tk.X, pady=10)
        
        reset_btn = ttk.Button(apply_frame, text="Reset Parameters", command=self.reset_parameters)
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        apply_btn = ttk.Button(apply_frame, text="Apply Effect", command=self.apply_effect)
        apply_btn.pack(side=tk.RIGHT, padx=5)
        
    def create_display_area(self):
        # Tab control for different views
        self.tab_control = ttk.Notebook(self.right_frame)
        
        # Main view tab
        self.main_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.main_tab, text='Main View')
        
        # Comparison view tab
        self.comparison_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.comparison_tab, text='Side by Side')
        
        # Steps view tab
        self.steps_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.steps_tab, text='Process Steps')
        
        self.tab_control.pack(expand=1, fill='both')
        
        # Setup main view
        self.main_display = ttk.Label(self.main_tab)
        self.main_display.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        
        # Setup comparison view
        comparison_frame = ttk.Frame(self.comparison_tab)
        comparison_frame.pack(expand=True, fill=tk.BOTH)
        
        self.original_display = ttk.Label(comparison_frame)
        self.original_display.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5, pady=5)
        
        self.cartoon_display = ttk.Label(comparison_frame)
        self.cartoon_display.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=5, pady=5)
        
        # Setup steps view (will be populated when processing an image)
        self.steps_frame = ttk.Frame(self.steps_tab)
        self.steps_frame.pack(expand=True, fill=tk.BOTH)
        
    def create_status_bar(self):
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT, padx=5)
        
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            status_frame, variable=self.progress_var, mode="determinate", length=200
        )
        self.progress_bar.pack(side=tk.RIGHT, padx=5, pady=2)
        
    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff")]
        )
        if file_path:
            try:
                self.status_var.set(f"Loading image: {os.path.basename(file_path)}")
                self.progress_var.set(10)
                self.root.update_idletasks()
                
                # Load the image using OpenCV
                img = cv2.imread(file_path)
                if img is None:
                    raise ValueError("Could not load the image")
                
                self.progress_var.set(50)
                self.root.update_idletasks()
                
                # Resize for display if needed
                img = self.cartoon_filter.resize_image(img)
                
                self.original_image = img.copy()
                self.current_image = img.copy()
                
                self.progress_var.set(80)
                self.root.update_idletasks()
                
                # Display the original image
                self.update_displays(original=self.original_image)
                
                self.progress_var.set(100)
                self.status_var.set(f"Loaded: {os.path.basename(file_path)}")
                
                # Clear any previous cartoon result
                self.cartoon_result = None
                
                # Apply initial effect with current parameters
                self.apply_effect()
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not load image: {str(e)}")
                self.status_var.set("Error loading image")
                self.progress_var.set(0)
    
    def update_parameters(self):
        # Update the cartoon filter with the current UI values
        self.cartoon_filter.edge_detection_method = self.edge_method_var.get()
        self.cartoon_filter.canny_threshold1 = self.threshold1_var.get()
        self.cartoon_filter.canny_threshold2 = self.threshold2_var.get()
        self.cartoon_filter.edge_blur = self.edge_blur_var.get()
        self.cartoon_filter.line_size = self.line_size_var.get()
        
        self.cartoon_filter.edge_preserve = self.edge_preserve_var.get()
        self.cartoon_filter.bilateral_d = self.bilateral_d_var.get()
        self.cartoon_filter.bilateral_sigma_color = self.bilateral_sigma_color_var.get()
        self.cartoon_filter.bilateral_sigma_space = self.bilateral_sigma_space_var.get()
        
        self.cartoon_filter.quantization_method = self.quant_method_var.get()
        self.cartoon_filter.num_colors = self.num_colors_var.get()
        self.cartoon_filter.saturation_factor = self.saturation_var.get()
        
    def update_preview(self, event=None):
        if self.is_processing or self.original_image is None:
            return
            
        # If a thread is already running, we don't want to start another
        if self.processing_thread and self.processing_thread.is_alive():
            return
            
        # Update parameters and start processing thread
        self.update_parameters()
        self.processing_thread = threading.Thread(target=self.process_image)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
    def process_image(self):
        self.is_processing = True
        self.status_var.set("Processing image...")
        self.progress_var.set(20)
        
        try:
            if self.original_image is not None:
                # Apply the cartoon effect
                self.cartoon_result = self.cartoon_filter.apply_cartoon_effect(self.original_image)
                self.progress_var.set(80)
                
                # Update the display
                self.update_displays(
                    original=self.original_image, 
                    cartoon=self.cartoon_result['cartoon']
                )
                
                # Update the steps display
                self.update_steps_display()
                
                self.progress_var.set(100)
                self.status_var.set("Processing complete")
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
        finally:
            self.is_processing = False
    
    def update_displays(self, original=None, cartoon=None):
        if original is not None:
            # Update main display
            if cartoon is None:
                img_display = self.cartoon_filter.get_cv2_image_for_tk(original)
                self.main_display.config(image=img_display)
                self.main_display.image = img_display
            else:
                img_display = self.cartoon_filter.get_cv2_image_for_tk(cartoon)
                self.main_display.config(image=img_display)
                self.main_display.image = img_display
                
            # Update comparison display
            original_img = self.cartoon_filter.get_cv2_image_for_tk(original)
            self.original_display.config(image=original_img)
            self.original_display.image = original_img
            
            if cartoon is not None:
                cartoon_img = self.cartoon_filter.get_cv2_image_for_tk(cartoon)
                self.cartoon_display.config(image=cartoon_img)
                self.cartoon_display.image = cartoon_img
    
    def update_steps_display(self):
        # Clear previous widgets in steps tab
        for widget in self.steps_frame.winfo_children():
            widget.destroy()
            
        if self.cartoon_result is None:
            return
            
        # Create a figure for the steps visualization
        fig = plt.figure(figsize=(10, 8), dpi=100)
        
        # Plot all steps in the process
        plt.subplot(221)
        plt.title("Original Image")
        plt.imshow(cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        
        plt.subplot(222)
        plt.title("Bilateral Filtering")
        plt.imshow(cv2.cvtColor(self.cartoon_result['filtered'], cv2.COLOR_BGR2RGB))
        plt.axis('off')
        
        plt.subplot(223)
        plt.title("Edge Detection")
        plt.imshow(self.cartoon_result['edges'], cmap='gray')
        plt.axis('off')
        
        plt.subplot(224)
        plt.title("Final Cartoon")
        plt.imshow(cv2.cvtColor(self.cartoon_result['cartoon'], cv2.COLOR_BGR2RGB))
        plt.axis('off')
        
        plt.tight_layout()
        
        # Add the figure to the tab
        canvas = FigureCanvasTkAgg(fig, master=self.steps_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def apply_effect(self):
        if self.original_image is None:
            messagebox.showinfo("Info", "Please load an image first")
            return
            
        # Update parameters
        self.update_parameters()
        
        # Start processing
        self.status_var.set("Applying cartoon effect...")
        self.progress_var.set(0)
        
        # Process in a thread to prevent UI freezing
        self.processing_thread = threading.Thread(target=self.process_image)
        self.processing_thread.daemon = True
        self.processing_thread.start()
    
    def save_cartoon(self):
        if self.cartoon_result is None or 'cartoon' not in self.cartoon_result:
            messagebox.showinfo("Info", "Apply cartoon effect first")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.status_var.set("Saving image...")
                self.progress_var.set(30)
                
                # Save the cartoon result
                cv2.imwrite(file_path, self.cartoon_result['cartoon'])
                
                self.progress_var.set(100)
                self.status_var.set(f"Saved to: {os.path.basename(file_path)}")
                
                messagebox.showinfo("Success", f"Image saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save image: {str(e)}")
                self.status_var.set("Error saving image")
                self.progress_var.set(0)
    
    def batch_process(self):
        # Ask user for input folder
        input_dir = filedialog.askdirectory(title="Select input folder with images")
        if not input_dir:
            return
            
        # Ask user for output folder
        output_dir = filedialog.askdirectory(title="Select output folder for cartoon images")
        if not output_dir:
            return
            
        # Update parameters
        self.update_parameters()
        
        # Get list of image files
        image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff')
        image_files = [f for f in os.listdir(input_dir) 
                       if os.path.isfile(os.path.join(input_dir, f)) 
                       and f.lower().endswith(image_extensions)]
        
        if not image_files:
            messagebox.showinfo("Info", "No image files found in the selected folder")
            return
            
        # Confirm with user
        confirm = messagebox.askyesno(
            "Confirm Batch Process", 
            f"Found {len(image_files)} images. Process all with current settings?"
        )
        
        if not confirm:
            return
            
        # Process images in a thread
        threading.Thread(
            target=self.batch_process_thread, 
            args=(input_dir, output_dir, image_files)
        ).start()
    
    def batch_process_thread(self, input_dir, output_dir, image_files):
        total_files = len(image_files)
        processed = 0
        
        for filename in image_files:
            try:
                self.status_var.set(f"Processing {processed+1}/{total_files}: {filename}")
                self.progress_var.set((processed / total_files) * 100)
                
                # Load image
                input_path = os.path.join(input_dir, filename)
                img = cv2.imread(input_path)
                
                if img is None:
                    continue
                    
                # Apply cartoon effect
                result = self.cartoon_filter.apply_cartoon_effect(img)
                
                # Save result
                output_name = os.path.splitext(filename)[0] + "_cartoon.png"
                output_path = os.path.join(output_dir, output_name)
                cv2.imwrite(output_path, result['cartoon'])
                
                processed += 1
                time.sleep(0.1)  # Small delay to update UI
                
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                
        self.status_var.set(f"Batch processing complete. Processed {processed}/{total_files} images")
        self.progress_var.set(100)
        messagebox.showinfo("Batch Complete", f"Processed {processed}/{total_files} images")
    
    def reset_parameters(self):
        # Reset the cartoon filter
        self.cartoon_filter = CartoonFilter()
        
        # Reset UI elements
        self.edge_method_var.set(self.cartoon_filter.edge_detection_method)
        self.threshold1_var.set(self.cartoon_filter.canny_threshold1)
        self.threshold2_var.set(self.cartoon_filter.canny_threshold2)
        self.edge_blur_var.set(self.cartoon_filter.edge_blur)
        self.line_size_var.set(self.cartoon_filter.line_size)
        
        self.edge_preserve_var.set(self.cartoon_filter.edge_preserve)
        self.bilateral_d_var.set(self.cartoon_filter.bilateral_d)
        self.bilateral_sigma_color_var.set(self.cartoon_filter.bilateral_sigma_color)
        self.bilateral_sigma_space_var.set(self.cartoon_filter.bilateral_sigma_space)
        
        self.quant_method_var.set(self.cartoon_filter.quantization_method)
        self.num_colors_var.set(self.cartoon_filter.num_colors)
        self.saturation_var.set(self.cartoon_filter.saturation_factor)
        
        # Update preview if image is loaded
        if self.original_image is not None:
            self.update_preview()
    
    def on_window_resize(self, event=None):
        # Update image display when window is resized
        if self.original_image is not None and self.cartoon_result is not None:
            self.update_displays(original=self.original_image, cartoon=self.cartoon_result['cartoon'])


    def apply_preset(self, event=None):
        """Apply the selected preset to the cartoon filter"""
        preset_name = self.preset_var.get()
        if preset_name:
            # Apply the preset to the cartoon filter
            success = self.preset_loader.apply_preset(self.cartoon_filter, preset_name)
            
            if success:
                # Update UI values to match the preset
                self.edge_method_var.set(self.cartoon_filter.edge_detection_method)
                self.threshold1_var.set(self.cartoon_filter.canny_threshold1)
                self.threshold2_var.set(self.cartoon_filter.canny_threshold2)
                self.edge_blur_var.set(self.cartoon_filter.edge_blur)
                self.line_size_var.set(self.cartoon_filter.line_size)
                
                self.edge_preserve_var.set(self.cartoon_filter.edge_preserve)
                self.bilateral_d_var.set(self.cartoon_filter.bilateral_d)
                self.bilateral_sigma_color_var.set(self.cartoon_filter.bilateral_sigma_color)
                self.bilateral_sigma_space_var.set(self.cartoon_filter.bilateral_sigma_space)
                
                self.quant_method_var.set(self.cartoon_filter.quantization_method)
                self.num_colors_var.set(self.cartoon_filter.num_colors)
                self.saturation_var.set(self.cartoon_filter.saturation_factor)
                
                # Apply effect to image if one is loaded
                if self.original_image is not None:
                    self.apply_effect()
                    
                self.status_var.set(f"Applied preset: {preset_name}")
    
    def save_current_preset(self):
        """Save current settings as a new preset"""
        from tkinter import simpledialog
        
        # Get preset name from user
        preset_name = simpledialog.askstring("Save Preset", "Enter a name for the preset:")
        if preset_name:
            # Create a preset from current settings
            preset = create_preset_from_filter(self.cartoon_filter)
            
            # Save the preset
            success = self.preset_loader.save_preset(preset_name, preset)
            
            if success:
                # Update the preset combobox
                self.preset_combo["values"] = self.preset_loader.get_preset_names()
                self.preset_var.set(preset_name)
                self.status_var.set(f"Saved preset: {preset_name}")
            else:
                messagebox.showerror("Error", f"Could not save preset: {preset_name}")

# Main application entry point
if __name__ == "__main__":
    root = tk.Tk()
    app = CartoonApp(root)
    root.mainloop() 