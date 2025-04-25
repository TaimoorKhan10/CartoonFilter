# Cartoon Filter Application

A Python application that transforms regular photos into cartoon-style images using advanced image processing techniques.

## Features

- Convert photos into cartoon-style images with adjustable parameters
- Real-time preview of parameter changes
- Multiple edge detection methods (Canny, Sobel, Laplacian)
- Color quantization using K-means or uniform quantization
- Save and load preset styles
- Batch processing capability for multiple images
- Side-by-side comparison view
- Processing steps visualization

## Screenshots

(Add screenshots of your application here)

## Requirements

- Python 3.7+
- OpenCV
- NumPy
- PIL (Pillow)
- Matplotlib
- scikit-image

## Installation

1. Clone this repository:
```
git clone https://github.com/yourusername/cartoon-filter.git
cd cartoon-filter
```

2. Install required packages:
```
pip install -r requirements.txt
```

## Usage

### GUI Application

To start the main application with full features:

```
python main.py
```

### Command Line Interface

For batch processing or automation:

```
python cli.py -i input_image.jpg -o output_image.png
```

Use `python cli.py --help` for more options.

## How It Works

The cartoon effect is created through several image processing steps:

1. **Edge Detection**: Identifies outlines in the image using methods like Canny, Sobel, or Laplacian
2. **Bilateral Filtering**: Smooths the image while preserving edges
3. **Color Quantization**: Reduces the number of colors to create flat color regions
4. **Color Enhancement**: Saturates colors to make them more vibrant

The combination of these techniques creates the cartoon-like appearance.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenCV for providing powerful image processing libraries
- The Python community for creating excellent documentation and examples 