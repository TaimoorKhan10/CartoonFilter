# Advanced Cartoon Filter

A comprehensive Python application that transforms regular images into cartoon-style renditions using classical digital image processing techniques.

## Features

- **Multiple Edge Detection Methods**:
  - Canny Edge Detection
  - Sobel Edge Detection
  - Laplacian Edge Detection

- **Advanced Color Processing**:
  - Bilateral Filtering for Edge Preservation
  - Color Quantization (K-means & Uniform)
  - Saturation Enhancement

- **Interactive GUI**:
  - Real-time parameter adjustment
  - Side-by-side comparison view
  - Step-by-step process visualization
  - Batch processing capabilities

- **Batch Processing**:
  - Process multiple images at once
  - Save processing metrics

## Requirements

- Python 3.6+
- OpenCV
- NumPy
- Pillow
- Matplotlib
- scikit-image
- tkinter

## Installation

1. Clone this repository:
   ```
   git clone https://your-repository-url.git
   cd CartoonFilter
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Running the Application

To launch the application, run:

```
python main.py
```

### Using the Interface

1. **Load an Image**: Click "Load Image" to select an image file
2. **Adjust Parameters**: Modify the edge detection, bilateral filter, and color quantization parameters
3. **View Results**: Switch between the main view, comparison view, and process steps tabs
4. **Save Your Work**: Save the cartoonized image using the "Save Cartoon" button

### Batch Processing

To process multiple images at once:

1. Click "Batch Process"
2. Select the input folder containing images
3. Select the output folder for the cartoonized images
4. Confirm the processing

## Technical Details

### Image Processing Pipeline

1. **Edge Detection**:
   - Converts image to grayscale
   - Applies Gaussian blur for noise reduction
   - Detects edges using the selected method (Canny, Sobel, or Laplacian)
   - Dilates edges for more pronounced lines

2. **Bilateral Filtering**:
   - Applies edge-preserving smoothing
   - Reduces noise while preserving important edges

3. **Color Quantization**:
   - Reduces the number of colors using K-means or uniform quantization
   - Creates the characteristic "flat" cartoon look

4. **Saturation Enhancement**:
   - Increases color saturation for a more vibrant cartoon appearance

5. **Edge Overlay**:
   - Combines the detected edges with the processed color image
   - Creates the final cartoon effect

## Customization

The application offers extensive customization options:

- **Edge Detection Parameters**:
  - Method selection
  - Threshold values
  - Edge blur amount
  - Line thickness

- **Bilateral Filter Parameters**:
  - Filter diameter
  - Color sigma
  - Space sigma
  - Edge preservation toggle

- **Color Quantization Parameters**:
  - Method selection
  - Number of colors
  - Saturation level

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 