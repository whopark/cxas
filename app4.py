import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import glob
import cv2
import re
from scipy.ndimage import gaussian_filter

class Rib3DApp:
    def __init__(self, root):
        self.root = root
        self.root.title('3D Volumetric Rib Cage & Fracture Visualization')
        self.root.geometry('950x700')

        self.loaded_folder = None
        self.rib_files = {}
        self.current_result_img = None

        # Top Control Frame
        self.ctrl_frame = tk.Frame(root)
        self.ctrl_frame.pack(side=tk.TOP, pady=10, fill=tk.X)

        self.load_btn = tk.Button(self.ctrl_frame, text='1. Select Outputs Folder', command=self.load_folder)
        self.load_btn.pack(side=tk.LEFT, padx=10)

        tk.Label(self.ctrl_frame, text="Suspected Fractures:").pack(side=tk.LEFT, padx=5)
        self.fracture_entry = tk.Entry(self.ctrl_frame, width=20)
        self.fracture_entry.pack(side=tk.LEFT, padx=5)

        self.render_btn = tk.Button(self.ctrl_frame, text='2. Generate 3D Rib', command=self.render_ribs, state=tk.DISABLED)
        self.render_btn.pack(side=tk.LEFT, padx=10)

        self.save_btn = tk.Button(self.ctrl_frame, text='3. Save Render', command=self.save_render, state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, padx=10)

        self.status_label = tk.Label(root, text='Waiting for folder selection...', fg='blue')
        self.status_label.pack(side=tk.TOP, pady=5)

        self.canvas = tk.Canvas(root, width=512, height=512, bg='black')
        self.canvas.pack(pady=10)

    def load_folder(self):
        folder_path = filedialog.askdirectory(title="Select folder with segmentation masks")
        if not folder_path:
            return
        
        search_pattern = os.path.join(folder_path, '*rib*.png')
        files = glob.glob(search_pattern)
        
        if not files:
            messagebox.showerror('No Ribs Found', f'No *rib*.png files found in {folder_path}')
            return
            
        self.loaded_folder = folder_path
        self.rib_files = {os.path.basename(f).lower(): f for f in files}
        self.render_btn.config(state=tk.NORMAL)
        self.save_btn.config(state=tk.DISABLED)
        self.status_label.config(text=f'Loaded {len(self.rib_files)} rib masks from {os.path.basename(folder_path)}.')

        # 1. 새 폴더 선택 시 기존 이미지 및 캔버스 지워서 초기화
        self.canvas.delete("all")
        self.current_result_img = None

        if not self.fracture_entry.get():
            self.fracture_entry.insert(0, "posterior 5th, anterior 6th")

    def render_ribs(self):
        if not self.rib_files:
            return
            
        self.status_label.config(text='기하학적 3D 볼륨 렌더링 중입니다... 잠시만 기다려주세요 (약 3~10초 소요)')
        self.root.update()
        
        try:
            first_path = list(self.rib_files.values())[0]
            first_img = cv2.imread(first_path, cv2.IMREAD_GRAYSCALE)
            height, width = first_img.shape
            
            composite = np.zeros((height, width, 3), dtype=np.float32)
            z_buffer = np.zeros((height, width), dtype=np.float32) - 1000

            L = np.array([-0.5, 0.5, 1.0])
            L = L / np.linalg.norm(L)
            
            fractures = [f.strip().lower() for f in self.fracture_entry.get().split(',') if f.strip()]
            labels_to_draw = []
            
            for name, path in self.rib_files.items():
                mask = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                if mask is None or mask.max() == 0: continue
                
                dist = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
                max_v = dist.max()
                if max_v == 0: continue
                
                # 라벨(갈비뼈 번호) 추출 및 등록
                match = re.search(r'(\d+)(st|nd|rd|th)', name)
                if match:
                    number_str = match.group(1)
                    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(dist) # 갈비뼈 중 가장 두꺼운 중심부를 Text 표기 영역으로 탐색
                    labels_to_draw.append((maxLoc, number_str))
                
                dist = gaussian_filter(dist, sigma=2)
                z = dist * 1.5
                
                gy, gx = np.gradient(z)
                gz = np.ones_like(z)
                
                norm = np.sqrt(gx**2 + gy**2 + gz**2) + 0.0001
                nx = gx / norm
                ny = gy / norm
                nz = gz / norm
                
                light_intensity = nx * L[0] + ny * L[1] + nz * L[2]
                light_intensity = np.clip(light_intensity, 0, 1)
                
                ambient = 0.3
                diffuse = 0.7 * light_intensity
                specular = 0.4 * np.power(light_intensity, 8)
                total_light = ambient + diffuse + specular
                
                is_frac = any(frac in name for frac in fractures) if fractures else False
                
                if is_frac:
                    base_color = np.array([255, 30, 30])
                elif 'posterior' in name:
                    base_color = np.array([160, 170, 180])
                else:
                    base_color = np.array([240, 245, 250])
                    
                color_img = np.zeros((height, width, 3), dtype=np.float32)
                color_img[:, :, 0] = base_color[0] * total_light
                color_img[:, :, 1] = base_color[1] * total_light
                color_img[:, :, 2] = base_color[2] * total_light
                
                if 'posterior' in name: base_z = 10
                elif 'anterior' in name: base_z = 40
                else: base_z = 25
                
                if is_frac:
                    base_z += 5
                    color_img += 30
                    
                current_z = base_z + z
                
                update_mask = (mask > 0) & (current_z > z_buffer)
                
                composite[update_mask] = color_img[update_mask]
                z_buffer[update_mask] = current_z[update_mask]
                
            composite = np.clip(composite, 0, 255).astype(np.uint8)
            
            # 3. 텍스트 라벨 (갈비뼈 번호) 후행 그리기 로직 (폰트/사이즈 적용)
            for (pt, txt) in labels_to_draw:
                # 외곽선을 위해 검은색 폰트를 먼저 굵게 찍음
                cv2.putText(composite, txt, (pt[0]-25, pt[1]+20), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 0), 10)
                # 내부에 밝은 색상 글씨 레이어
                cv2.putText(composite, txt, (pt[0]-25, pt[1]+20), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 120), 4)
            
            result_img = Image.fromarray(composite)
            
            self.current_result_img = result_img
            self.save_btn.config(state=tk.NORMAL)
            
            display_img = result_img.copy()
            display_img.thumbnail((512, 512), Image.Resampling.LANCZOS)
            
            self.photo = ImageTk.PhotoImage(display_img)
            self.canvas.delete("all")
            self.canvas.create_image(256, 256, image=self.photo)
            
            self.status_label.config(text=f'완벽한 3D 뼈대 렌더링 완료! 붉은 영역은 골절 부위입니다.')
            
        except Exception as e:
            self.status_label.config(text=f'Error rendering: {e}')
            import traceback
            traceback.print_exc()

    def save_render(self):
        # 2. 렌더링 결과 이미지 저장 기능
        if not self.current_result_img:
            return
            
        save_path = filedialog.asksaveasfilename(
            title="Save Rendered Image",
            defaultextension=".png",
            filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg"), ("All Files", "*.*")]
        )
        if save_path:
            try:
                self.current_result_img.save(save_path)
                self.status_label.config(text=f"Saved to {os.path.basename(save_path)}")
                messagebox.showinfo("Saved", f"3D 렌더링 이미지가 성공적으로 저장되었습니다!\n경로: {save_path}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save image:\n{e}")

if __name__ == '__main__':
    root = tk.Tk()
    app = Rib3DApp(root)
    root.mainloop()
