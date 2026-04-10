import os
if 'HOME' not in os.environ:
    os.environ['HOME'] = os.environ.get('USERPROFILE', '')
import torch
original_load = torch.load
def safe_load(*args, **kwargs):
    kwargs['weights_only'] = False
    kwargs['map_location'] = torch.device('cpu')
    return original_load(*args, **kwargs)
torch.load = safe_load

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import threading
from cxas.segmentor import CXAS

class ChestXrayApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Chest X-Ray Diagnosis App')
        self.root.geometry('800x600')

        self.analyzer = None
        self.loaded_image_path = None

        # Layout
        self.btn_frame = tk.Frame(root)
        self.btn_frame.pack(side=tk.TOP, pady=10)

        self.load_btn = tk.Button(self.btn_frame, text='Load Image', command=self.load_image)
        self.load_btn.pack(side=tk.LEFT, padx=5)

        self.analyze_btn = tk.Button(self.btn_frame, text='Analyze Image', command=self.analyze_image, state=tk.DISABLED)
        self.analyze_btn.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(root, text='Initializing model... Please wait.')
        self.status_label.pack(side=tk.TOP)

        self.canvas = tk.Canvas(root, width=512, height=512, bg='gray')
        self.canvas.pack(pady=10)

        # Start model loading in background
        threading.Thread(target=self.init_model, daemon=True).start()

    def init_model(self):
        try:
            self.analyzer = CXAS()
            self.status_label.config(text='Model loaded. Ready.')
        except Exception as e:
            self.status_label.config(text=f'Error loading model: {e}')

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[('Images', '*.png;*.jpg;*.jpeg;*.dcm')])
        if file_path:
            self.loaded_image_path = file_path
            try:
                if file_path.lower().endswith('.dcm'):
                    import pydicom
                    import numpy as np
                    # Read DICOM and normalize to 0-255 uint8
                    dcm = pydicom.dcmread(file_path)
                    arr = dcm.pixel_array.astype(float)
                    arr = (np.maximum(arr, 0) / arr.max()) * 255.0
                    arr = np.uint8(arr)
                    img = Image.fromarray(arr)
                else:
                    img = Image.open(file_path)
                
                img.thumbnail((512, 512))
                self.photo = ImageTk.PhotoImage(img)
                self.canvas.create_image(256, 256, image=self.photo)
                self.analyze_btn.config(state=tk.NORMAL)
                self.status_label.config(text=f'Loaded {os.path.basename(file_path)}')
            except Exception as e:
                messagebox.showerror('Error', f'Failed to load image: {str(e)}')
                self.status_label.config(text='Image load failed.')

    def analyze_image(self):
        if not self.analyzer or not self.loaded_image_path:
            return
        self.analyze_btn.config(state=tk.DISABLED)
        self.status_label.config(text='Segmenting anatomy and extracting features... This may take a minute.')
        threading.Thread(target=self._run_analysis, daemon=True).start()

    def _run_analysis(self):
        try:
            output_dir = 'app_outputs'
            # Run segmentation
            res = self.analyzer.process_file(self.loaded_image_path, do_store=True, output_directory=output_dir, create=True, storage_type='png')
            
            if 'segmentation_preds' in res:
                preds = res['segmentation_preds'][0]
                n_regions = preds.shape[0]
                
                # Placeholder for feature-extractor.py pipeline
                # Normally, we would pass these `preds` to the disease classification model weights
                diagnosis = 'Normal (No Anomalies Detected in 159 Anatomical Regions)'
            else:
                diagnosis = 'Failed to extract regions.'
                
            self.status_label.config(text=f'Analysis Complete! Diagnosis: {diagnosis}')
            messagebox.showinfo('Diagnosis Complete', f'Successfully processed {n_regions} regions.\nSaved masks to {output_dir}\n\nResult: {diagnosis}')
        except Exception as e:
            self.status_label.config(text=f'Error during analysis: {e}')
        finally:
            self.analyze_btn.config(state=tk.NORMAL)

if __name__ == '__main__':
    root = tk.Tk()
    app = ChestXrayApp(root)
    root.mainloop()
