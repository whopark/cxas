# CXAS Applications Tutorial

Welcome! This tutorial will guide you through using the customized Chest X-Ray applications (`app2.py` and `app3.py`) to easily segment and analyze Chest X-ray DICOMs and images.

---

## 1. Using `app2.py` (Single File Processing)

Use this when you have a specific patient's scan (e.g. `patient_001.dcm`) and you want to analyze it and keep its segmentations in a neat, isolated folder.

### Step-by-Step
1. Run the app in your terminal/command prompt:
   ```bash
   python app2.py
   ```
2. The user interface will appear. Click **`Load DICOM Image`**.
3. Browse your computer and select a Chest X-ray file (it supports `.dcm`, `.png`, `.jpg`).
4. Wait a moment for the preview image to load inside the canvas.
5. Click **`Analyze Image`**.
6. The app will extract the original filename (e.g., `patient_001`). It then automatically creates a new folder in your project directory at `app_outputs/patient_001/`.
7. Once finished, open that folder to find all 159 segmentation masks reliably isolated.

---

## 2. Using `app3.py` (Batch Dataset Processing)

Use this when you have a large dataset of X-rays stored in a single folder (or sub-folders) and want an automated way to process all of them without clicking each file.

### Step-by-Step
1. Run the application:
   ```bash
   python app3.py
   ```
2. In the GUI, click **`Load Folder`**.
3. A folder selection window will appear. Choose the root folder containing your images. 
   *(Note: The app will deeply scan this folder and all of its sub-directories to find suitable images).*
4. The status label will indicate how many images were found. (e.g., `Loaded folder: dataset (500 images found)`).
5. Click **`Analyze All Images`**.
6. **Sit back and wait!** The program will iterate through the images. For each image (e.g., `chest_A.png`, `chest_B.dcm`):
   - It creates `app_outputs/chest_A/` and `app_outputs/chest_B/`.
   - Runs the heavy AI segmentation specifically into those folders.
7. You can monitor the progress on the screen (`Processing 45/500...`). Once finished, a confirmation popup will alert you.

---

## 3. Using `app4.py` (3D Rib Volumetric Rendering & Fracture Analysis)

Use this *after* you have processed images using `app2.py` or `app3.py`. `app4.py` serves as a dedicated **3D Visualizer** to rebuild independent 2D flat masks into a single, fully shaded Photorealistic 3D geometry interface without needing arbitrary 3D model structures.

### Step-by-Step
1. Run the application:
   ```bash
   python app4.py
   ```
2. Click **`1. Select Outputs Folder`** and choose a specific processed patient folder (`e.g., app_outputs/000001`). Note: Choosing a new folder will automatically reset the canvas and clear previous images.
3. Use the **`Suspected Fractures`** text box to target damaged bones. You can supply multiple keywords separated by commas (e.g., `posterior 5th, anterior 6th rib`). This text parsing is extremely flexible!
4. Click **`2. Generate 3D Rib Rendering`**. Wait about 3~10 seconds.
5. The script runs Distance Transforms and Phong Reflection equations across all relevant files to assign physical Z-depth, lighting, shadows, and smooth 3D bump mappings!
6. **Rib Numbers** (e.g. '5', '6') will be boldly generated at the thickest geometric center of each visible rib.
7. If you assigned any fractures, those exact ribs will aggressively glow **RED** inside the volume.
8. Click **`3. Save Render`** to permanently export your new 3D view as a high-resolution PNG image!

---

## Output Structure Example
After using `app3.py` on a given folder, your working directory will safely have the following structure:
```text
cxas/
├── app3.py
└── app_outputs/
    ├── patient_1/
    │   ├── 0_rib_1.png
    │   ├── 1_rib_2.png...
    ├── patient_2/
    │   ├── 0_rib_1.png...
```
*(Outputs are automatically git-ignored so you won't accidentally commit thousands of 512x512 mask images to GitHub).*
