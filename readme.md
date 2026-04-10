# Chest X-Ray Anatomy Segmentation (CXAS) Application

This project provides a set of Graphical User Interface (GUI) applications for analyzing Chest X-ray images, built around the [CXAS (Chest X-ray Anatomy Segmentation)](https://github.com/ConstantinSeibold/CXAS) framework.

## Features

The project includes three distinct applications to suit different analysis needs:

1. **`app.py`**: A basic application to load a single image (PNG/JPG/DCM) and perform the base anatomy segmentation.
2. **`app2.py`**: An enhanced single-file processor. It allows you to select a DICOM or image file, automatically creates an output directory named after the file (`app_outputs/<filename>/`), and saves all extracted segmentations inside it for clean organization.
3. **`app3.py`**: A powerful batch-processing application. You can load an entire folder containing multiple images or DICOMs. The app recursively scans for all valid images and automatically runs segmentation for each one, sorting the output masks into individual folders per image.
4. **`app4.py`**: A built-in true 3D graphics rendering GUI. This app loads an folder of `app3.py` outputs and uses OpenCV and Phong reflection mathematics to morph flat 2D rib masks into photorealistic 3D bone renders natively. It includes features for highlighting suspected fractures and auto-numbering ribs dynamically.

## Installation & Setup

1. It is recommended to use **Python 3.11 or 3.12** since older dependencies like `pydicom-seg` require `numpy < 2.0.0` which can cause build issues on Python 3.13 without C++ build tools.
2. Clone this repository:
   ```bash
   git clone https://github.com/whopark/cxas.git
   cd cxas
   ```
3. Install the required packages (and forcibly ignore pip dependency conflicts if you are using newer Python versions):
   ```bash
   pip install cython torch gdown torchvision numpy SimpleITK pydicom==2.0.0 scikit-image scikit-learn opencv-python colorcet pycocotools pandas tqdm "jsonschema>=3.2.0,<4.0.0"
   pip install pydicom-seg==0.4.1 cxas --no-deps
   ```

## Usage

Run any of the applications natively via python:
```bash
python app3.py
```

For more detailed usage instructions, please refer to the [tutorial.md](tutorial.md) file.
