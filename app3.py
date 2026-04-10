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
import glob

class ChestXrayBatchApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Chest X-Ray Batch Diagnosis App')
        self.root.geometry('800x600')

        self.analyzer = None
        self.loaded_folder_path = None
        self.image_files = []

        # Layout
        self.btn_frame = tk.Frame(root)
        self.btn_frame.pack(side=tk.TOP, pady=10)

        self.load_btn = tk.Button(self.btn_frame, text='Load Folder', command=self.load_folder)
        self.load_btn.pack(side=tk.LEFT, padx=5)

        self.analyze_btn = tk.Button(self.btn_frame, text='Analyze All Images', command=self.analyze_images, state=tk.DISABLED)
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

    def load_folder(self):
        folder_path = filedialog.askdirectory(title="Select Folder with Images")
        if folder_path:
            self.loaded_folder_path = folder_path
            valid_exts = ('.dcm', '.png', '.jpg', '.jpeg')
            self.image_files = []
            
            # Recursively find all images
            for root_dir, dirs, files in os.walk(folder_path):
                for f in files:
                    if f.lower().endswith(valid_exts):
                        self.image_files.append(os.path.join(root_dir, f))
                        
            if not self.image_files:
                messagebox.showwarning('No Images Found', f'No valid images (.dcm, .png, .jpg, .jpeg) found in {folder_path}')
                self.status_label.config(text='Folder load failed (No images).')
                self.canvas.delete("all")
                self.analyze_btn.config(state=tk.DISABLED)
                return

            self.analyze_btn.config(state=tk.NORMAL)
            self.status_label.config(text=f'Loaded folder: {os.path.basename(folder_path)} ({len(self.image_files)} images found)')
            
            # Preview the first image just to show something
            first_img_path = self.image_files[0]
            try:
                if first_img_path.lower().endswith('.dcm'):
                    import pydicom
                    import numpy as np
                    dcm = pydicom.dcmread(first_img_path)
                    arr = dcm.pixel_array.astype(float)
                    arr = (np.maximum(arr, 0) / arr.max()) * 255.0
                    arr = np.uint8(arr)
                    img = Image.fromarray(arr)
                else:
                    img = Image.open(first_img_path)
                
                img.thumbnail((512, 512))
                self.photo = ImageTk.PhotoImage(img)
                self.canvas.delete("all")
                self.canvas.create_image(256, 256, image=self.photo)
            except Exception as e:
                print(f"Failed to load preview for {first_img_path}: {e}")

    def analyze_images(self):
        if not self.analyzer or not self.image_files:
            return
        self.analyze_btn.config(state=tk.DISABLED)
        self.load_btn.config(state=tk.DISABLED)
        self.status_label.config(text='Starting batch analysis... Please wait.')
        threading.Thread(target=self._run_analysis, daemon=True).start()

    def _run_analysis(self):
        total = len(self.image_files)
        success_count = 0
        try:
            for idx, img_path in enumerate(self.image_files):
                # Update status
                self.status_label.config(text=f'Processing {idx+1}/{total}: {os.path.basename(img_path)}...')
                
                # Fix for CXAS Windows path bug: replace backslashes with forward slashes
                # This prevents CXAS from misinterpreting the filename and creating nested directories like root/dcm/000001
                img_path_for_cxas = img_path.replace('\\', '/')
                
                # We just pass 'app_outputs' as the base target.
                # CXAS will automatically create a folder named after the file (e.g., app_outputs/000001)
                # because it internally does: outdir = os.path.join(outdir, filename)
                output_dir = 'app_outputs'
                os.makedirs(output_dir, exist_ok=True)
                
                try:
                    # Run segmentation
                    res = self.analyzer.process_file(img_path_for_cxas, do_store=True, output_directory=output_dir, create=True, storage_type='png')
                    if 'segmentation_preds' in res:
                        success_count += 1
                except Exception as e:
                    print(f"Error processing {img_path}: {e}")
            
            self.status_label.config(text=f'Batch Analysis Complete! Saved {success_count}/{total} images.')
            messagebox.showinfo('Batch Complete', f'Successfully processed {success_count} out of {total} images.\n\n각 파일 이름으로 생성된 폴더 내부에\n결과물이 저장되었습니다! (위치: app_outputs)')
            
        except Exception as e:
            self.status_label.config(text=f'Error during batch analysis: {e}')
        finally:
            self.analyze_btn.config(state=tk.NORMAL)
            self.load_btn.config(state=tk.NORMAL)

if __name__ == '__main__':
    root = tk.Tk()
    app = ChestXrayBatchApp(root)
    root.mainloop()
