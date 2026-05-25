# game_manager.py

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random, os, datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from logic import generate_magic_square, rotate_grid
from constants import get_fillers, LANG_DB, BTN_STYLES 

import json

class GameManager:
    def __init__(self, master_card, on_cancel_callback, on_finish_callback, get_lang_func):
        self.card = master_card
        self.on_cancel = on_cancel_callback
        self.on_finish = on_finish_callback
        self.get_lang = get_lang_func
        self.start_time = None
        self.elapsed_time = 0
        self.timer_running = False
        
        self.n = 3
        self.move_count = 0
        self.hint_count = 0  
        self.selected = None
        self.undo_stack = []
        self.image_pieces = {}
        self.tk_images = []
        self.mode = "English" 
        self.visual_style = "Image" 
        
        self.top_bar = ctk.CTkFrame(self.card, fg_color="transparent")
        self.top_bar.pack(fill="x", pady=(20, 10), padx=30)

        # [แก้ไขใช้ BTN_STYLES]
        self.btn_debug = ctk.CTkButton(self.top_bar, text="DEV", width=40, height=20, 
                                       command=self.instant_win, **BTN_STYLES["game_dev"])
        self.btn_debug.pack(side="right", padx=5)
        
        # [แก้ไขใช้ BTN_STYLES]
        self.btn_back = ctk.CTkButton(self.top_bar, text="Cancel", width=90, height=35, 
                                      command=self.on_cancel, **BTN_STYLES["game_cancel"])
        self.btn_back.pack(side="left")

        # [แก้ไขใช้ BTN_STYLES]
        self.btn_shuffle = ctk.CTkButton(self.top_bar, text="Shuffle", width=90, height=35, 
                                         command=self.shuffle_board, **BTN_STYLES["game_shuffle"])
        self.btn_shuffle.pack(side="left", padx=15)
        
        self.status_frame = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        self.status_frame.pack(side="right", padx=10)

        self.lbl_moves = ctk.CTkLabel(self.status_frame, text="Moves : 0", font=("Garamond", 18), text_color="black")
        self.lbl_moves.pack(anchor="e")
        self.lbl_target = ctk.CTkLabel(self.status_frame, text="Target : 15", font=("Garamond", 18), text_color="black")
        self.lbl_target.pack(anchor="e")
        self.lbl_timer = ctk.CTkLabel(self.status_frame, text="Time : 00:00", font=("Garamond", 18), text_color="black")
        self.lbl_timer.pack(anchor="e")

        self.canvas = tk.Canvas(self.card, bg="white", highlightthickness=0, borderwidth=0, bd=0)
        self.canvas.pack(fill="both", expand=True, padx=40, pady=5)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Configure>", lambda e: self.redraw())

        self.win_status_label = ctk.CTkLabel(self.card, text="", font=("Garamond", 20, "bold"), text_color="#2e7d32")
        self.win_status_label.pack(pady=5)
        
        self.bottom_bar = ctk.CTkFrame(self.card, fg_color="transparent")
        self.bottom_bar.pack(fill="x", pady=(5, 20))
        
        self.btn_hint = ctk.CTkButton(self.bottom_bar, text="Hint", command=self.give_hint, 
                                      width=130, height=40, **BTN_STYLES["game_hint"])
        self.btn_hint.pack(side="left", padx=20, expand=True)

        self.btn_undo = ctk.CTkButton(self.bottom_bar, text="Undo", command=self.undo, 
                                      width=130, height=40, **BTN_STYLES["game_undo"])
        self.btn_undo.pack(side="left", padx=20, expand=True)

        self.btn_submit = ctk.CTkButton(self.bottom_bar, text="Submit", command=self.submit_game, 
                                        width=130, height=40, **BTN_STYLES["game_submit"])
        self.btn_submit.pack(side="left", padx=20, expand=True)

    def start_new_game(self, name, size, mode, image_path, visual_style, arrange_mode="Random"):
        self.player_name = name
        self.n = size
        self.mode = mode
        self.visual_style = visual_style 
        self.arrange_mode = arrange_mode # <--- เก็บค่าเข้าคลาส
        
        self.image_pieces = {} 
        self.tk_images = []
        
        self.rotation_k = random.randint(0, 3)
        self.move_count = 0
        self.hint_count = 0 
        self.undo_stack.clear()
        self.selected = None
        
        self.win_status_label.configure(text="")
        self.game_won = False 
        self.elapsed_time = 0
        self.start_timer()

        M = self.n * (self.n * self.n + 1) // 2
        self.lbl_target.configure(text=f"Target : {M}")
        
        self.rebuild_mapping(name, mode)
        if image_path and self.visual_style == "Creative":
            self.process_image(image_path)
            
        self.shuffle_board()

    def process_image(self, image_path):
        if not image_path: return
        try:
            img = Image.open(image_path).convert("RGBA")
            min_dim = min(img.size)
            left = (img.width - min_dim) / 2
            top = (img.height - min_dim) / 2
            img = img.crop((left, top, left + min_dim, top + min_dim))
            img = img.resize((600, 600), Image.LANCZOS)
            
            piece_size = 600 // self.n
            for r in range(self.n):
                for c in range(self.n):
                    p_left, p_top = c * piece_size, r * piece_size
                    crop_img = img.crop((p_left, p_top, p_left + piece_size, p_top + piece_size))
                    
                    overlay = Image.new('RGBA', crop_img.size, (255, 255, 255, 25)) 
                    
                    final_piece = Image.alpha_composite(crop_img, overlay)
                    target_num = self.target_goal[r][c]
                    self.image_pieces[target_num] = final_piece
        except Exception as e:
            print(f"Error loading image: {e}")

    def rebuild_mapping(self, name, mode):
        base_target = generate_magic_square(self.n)
        self.target_goal = rotate_grid(base_target, self.rotation_k)
        fillers = get_fillers(mode)
        name_chars = list(name.upper()) if name else []
        char_sequence = name_chars.copy()
        idx = 0
        while len(char_sequence) < self.n * self.n:
            char_sequence.append(fillers[idx % len(fillers)])
            idx += 1
            
        arrange = getattr(self, 'arrange_mode', 'Random All')
        
        # 🌟 ตรวจสอบโหมดการเรียงตัวอักษร
        if arrange in ["Horizontal", "Vertical", "Diagonal"]:
            path_coords = []
            n = self.n
            
            # ขั้นตอนที่ 1: สร้างพิกัดพื้นฐาน (Base Coordinates) เริ่มจากมุมซ้ายบนปกติ
            if arrange == "Horizontal":     # แแนวนอนปกติ
                path_coords = [(r, c) for r in range(n) for c in range(n)]
            elif arrange == "Vertical":     # แนวตั้งปกติ
                path_coords = [(r, c) for c in range(n) for r in range(n)]
            elif arrange == "Diagonal":     # แนวเฉียงปกติ
                for d in range(2 * n - 1):
                    for r in range(max(0, d - n + 1), min(n, d + 1)):
                        path_coords.append((r, d - r))
            
            # ขั้นตอนที่ 2: 🎲 สุ่มการพลิกทิศทางเพื่อไม่ให้เด็กๆ เดาจุดเริ่มต้นได้
            flip_horizontal = random.choice([True, False])  # สุ่ม พลิกซ้าย-ขวา
            flip_vertical = random.choice([True, False])    # สุ่ม พลิกบน-ล่าง
            reverse_text = random.choice([True, False])     # สุ่ม อ่านจากหน้าไปหลัง หรือ หลังมาหน้า
            
            transformed_coords = []
            for r, c in path_coords:
                # คำนวณพิกัดใหม่ตามผลการสุ่มพลิกแกน
                new_r = (n - 1 - r) if flip_vertical else r
                new_c = (n - 1 - c) if flip_horizontal else c
                transformed_coords.append((new_r, new_c))
                
            # ถ้าสุ่มได้อ่านย้อนกลับ ให้พลิกลำดับของลิสต์พิกัด
            if reverse_text:
                transformed_coords.reverse()
                        
            # ขั้นตอนที่ 3: นำพิกัดที่ผ่านการสุ่มทิศทางแล้ว ไปจับคู่เข้าตารางเวทมนตร์
            path_nums = [self.target_goal[r][c] for r, c in transformed_coords]
            self.num_to_char = {path_nums[i]: char_sequence[i] for i in range(n * n)}
            
        else:
            # 🔀 โหมด Random All (ระบบเดิม: สุ่มกระจายทั่วไปหมด)
            all_nums = list(range(1, self.n * self.n + 1))
            random.shuffle(all_nums) 
            self.num_to_char = {num: char_sequence[i] for i, num in enumerate(all_nums)}

    def shuffle_board(self):
        nums = list(range(1, self.n * self.n + 1))
        random.shuffle(nums)
        self.current_nums = [nums[i*self.n : (i+1)*self.n] for i in range(self.n)]
        self.move_count = 0
        self.hint_count = 0 
        self.undo_stack.clear()
        self.selected = None
        self.redraw()

    def on_click(self, event):
        if getattr(self, 'game_won', False): return 
        if not hasattr(self, 'layout'): return
        x0, y0, cell = self.layout['x0'], self.layout['y0'], self.layout['cell']
        c, r = int((event.x - x0)//cell), int((event.y - y0)//cell)
        if 0 <= r < self.n and 0 <= c < self.n:
            if self.selected is None:
                self.selected = (r, c)
            else:
                r0, c0 = self.selected
                if (r0, c0) != (r, c):
                    self.undo_stack.append(((r0, c0), (r, c)))
                    self.current_nums[r0][c0], self.current_nums[r][c] = \
                        self.current_nums[r][c], self.current_nums[r0][c0]
                    self.move_count += 1
                self.selected = None
            self.redraw()

    def redraw(self):
        if not hasattr(self, 'current_nums'): return
        self.canvas.delete("all")
        self.canvas.update_idletasks() 
        texts = LANG_DB[self.get_lang()]
        W, H = self.canvas.winfo_width(), self.canvas.winfo_height()
        if W < 10: W, H = 550, 450
        n = self.n
        M = n * (n * n + 1) // 2
        cell = min((W - 120) / n, (H - 120) / n)
        x0, y0 = (W - n * cell) / 2, (H - n * cell) / 2
        self.layout = {'x0': x0, 'y0': y0, 'cell': cell}
        
        self.lbl_moves.configure(text=f"{texts['moves']} {self.move_count}")
        self.lbl_target.configure(text=f"{texts['target']} {M}")
        self.tk_images.clear() 

        for r in range(n):
            for c in range(n):
                x, y = x0 + c * cell, y0 + r * cell
                val = self.current_nums[r][c]
                char = self.num_to_char.get(val, "")
                
                # เช็คสถานะว่าเป็นโหมดรูปภาพหรือไม่
                is_image_mode = (self.visual_style == "Creative" and val in self.image_pieces)
                
                if is_image_mode:
                    resized_img = self.image_pieces[val].resize((int(cell), int(cell)), Image.LANCZOS)
                    tk_img = ImageTk.PhotoImage(resized_img)
                    self.tk_images.append(tk_img)
                    self.canvas.create_image(x, y, anchor="nw", image=tk_img)
                    
                    # ตีเส้นขอบจางๆ เพื่อแบ่งบล็อกภาพให้ชัดเจนขึ้น
                    self.canvas.create_rectangle(x, y, x+cell, y+cell, outline="#AEB6BF", width=1)
                    text_color = "white"
                else:
                    bg_colors = ["#EBF5FB", "#FEF9E7", "#EAFAF1", "#F4ECF7"]
                    base_bg = bg_colors[(r + c) % len(bg_colors)]
                    bg = base_bg if (r, c) != self.selected else "#FBEEE6"
                    self.canvas.create_rectangle(x, y, x+cell, y+cell, fill=bg, outline="#AEB6BF", width=1)
                    text_color = "#2E4053"
                
                # กรอบไฮไลท์สีแดงเมื่อเลือกช่อง
                if (r, c) == self.selected:
                    self.canvas.create_rectangle(x, y, x+cell, y+cell, outline="#FF7676", width=4)
                
                # --- การตั้งค่าฟอนต์และตำแหน่งแบบ Classic ---
                num_font = ("Garamond", int(cell * 0.15), "bold")
                char_font = ("Garamond", int(cell * 0.45), "bold")
                
                # y ของตัวเลขอยู่ด้านบน (0.2) / y ของตัวอักษรอยู่ตรงกลาง (0.55)
                num_y = y + cell * 0.2
                char_y = y + cell * 0.55
                
                # เสริม: หากเป็นโหมดรูปภาพ ให้วาดเงาสีดำด้านหลังข้อความ เพื่อกันกลืนกับพื้นหลัง
                if is_image_mode:
                    shadow_offset = max(1, int(cell * 0.02))
                    self.canvas.create_text(x + cell/2 + shadow_offset, num_y + shadow_offset, 
                                            text=str(val), font=num_font, fill="black")
                    self.canvas.create_text(x + cell/2 + shadow_offset, char_y + shadow_offset, 
                                            text=char, font=char_font, fill="black")

                # วาดข้อความจริงทับลงไป
                self.canvas.create_text(x + cell/2, num_y, text=str(val), font=num_font, fill=text_color)
                self.canvas.create_text(x + cell/2, char_y, text=char, font=char_font, fill=text_color)

        # วาดตัวเลขผลรวมรอบๆ กระดาน (เหมือนเดิม)
        row_sums = [sum(row) for row in self.current_nums]
        col_sums = [sum(self.current_nums[r][ci] for r in range(n)) for ci in range(n)]
        diag1_sum = sum(self.current_nums[i][i] for i in range(n))       
        diag2_sum = sum(self.current_nums[i][n-1-i] for i in range(n))   

        for i in range(n):
            self.canvas.create_text(x0 + n*cell + 25, y0 + i*cell + cell/2, text=str(row_sums[i]), fill=("#27AE60" if row_sums[i] == M else "#E74C3C"), font=("Garamond", 14, "bold"))
            self.canvas.create_text(x0 + i*cell + cell/2, y0 - 25, text=str(col_sums[i]), fill=("#27AE60" if col_sums[i] == M else "#E74C3C"), font=("Garamond", 14, "bold"))
        self.canvas.create_text(x0 - 35, y0 - 25, text=f"{diag1_sum} ↘", fill=("#27AE60" if diag1_sum == M else "#E74C3C"), font=("Garamond", 14, "bold"))
        self.canvas.create_text(x0 + n*cell + 35, y0 - 25, text=f"↙ {diag2_sum}", fill=("#27AE60" if diag2_sum == M else "#E74C3C"), font=("Garamond", 14, "bold"))
        self.check_win_status()

    def undo(self):
        if self.undo_stack:
            (r1, c1), (r2, c2) = self.undo_stack.pop()
            self.current_nums[r1][c1], self.current_nums[r2][c2] = self.current_nums[r2][c2], self.current_nums[r1][c1]
            self.move_count -= 1
            self.redraw()

    def give_hint(self):
        texts = LANG_DB[self.get_lang()]
        if self.hint_count >= 3:
            messagebox.showwarning(texts["hint_title"], texts["hint_msg"])
            return
        wrong_positions = [(r, c) for r in range(self.n) for c in range(self.n) if self.current_nums[r][c] != self.target_goal[r][c]]
        if not wrong_positions:
            messagebox.showinfo(texts["hint"], texts["hint_none"])
            return
        r_t, c_t = wrong_positions[0]
        correct_val = self.target_goal[r_t][c_t]
        for r in range(self.n):
            for c in range(self.n):
                if self.current_nums[r][c] == correct_val:
                    self.undo_stack.append(((r_t, c_t), (r, c)))
                    self.current_nums[r_t][c_t], self.current_nums[r][c] = self.current_nums[r][c], self.current_nums[r_t][c_t]
                    self.move_count += 1
                    self.hint_count += 1
                    self.redraw()
                    messagebox.showinfo(texts["hint"], texts["hint_success"].format(3 - self.hint_count))
                    return

    def check_win_status(self):
        n, M = self.n, self.n * (self.n * self.n + 1) // 2
        is_magic = (all(sum(r) == M for r in self.current_nums) and 
                    all(sum(self.current_nums[r][c] for r in range(n)) == M for c in range(n)) and
                    sum(self.current_nums[i][i] for i in range(n)) == M and
                    sum(self.current_nums[i][n-1-i] for i in range(n)) == M)
        if is_magic and not getattr(self, 'game_won', False):
            self.game_won = True
            self.timer_running = False
            texts = LANG_DB[self.get_lang()]
            self.win_status_label.configure(text=texts["magic_complete"])
            self.trigger_victory_effects()
            self.card.after(300, lambda: messagebox.showinfo(texts["win_title"], texts["win_msg"].format(self.player_name)))
        elif not is_magic:
            self.win_status_label.configure(text="")

    def trigger_victory_effects(self):
        self.particles = []
        W, H = self.canvas.winfo_width(), self.canvas.winfo_height()
        colors = ["#FF5733", "#33FF57", "#3357FF", "#F3FF33", "#FF33F3", "#00FFFF", "#FFD700"]
        centers = [(W*0.25, H*0.3), (W*0.5, H*0.2), (W*0.75, H*0.3)]
        for cx, cy in centers:
            for _ in range(40):
                p = {'x': cx, 'y': cy, 'vx': random.uniform(-6, 6), 'vy': random.uniform(-6, 2),   
                     'color': random.choice(colors), 'size': random.uniform(3, 8), 'life': random.randint(30, 60)}
                p['id'] = self.canvas.create_oval(cx, cy, cx+p['size'], cy+p['size'], fill=p['color'], outline="")
                self.particles.append(p)
        self.animate_fireworks()

    def animate_fireworks(self):
        if not hasattr(self, 'particles') or not self.particles: return
        active_particles = []
        for p in self.particles:
            p['life'] -= 1
            if p['life'] > 0:
                p['x'] += p['vx']; p['y'] += p['vy']; p['vy'] += 0.2  
                self.canvas.coords(p['id'], p['x'], p['y'], p['x']+p['size'], p['y']+p['size'])
                active_particles.append(p)
            else: self.canvas.delete(p['id'])
        self.particles = active_particles
        if self.particles: self.canvas.after(30, self.animate_fireworks)

    def update_ui_language(self):
        texts = LANG_DB[self.get_lang()]
        self.btn_back.configure(text=texts.get("cancel", "Cancel"))
        self.btn_shuffle.configure(text=texts.get("shuffle", "Shuffle"))
        self.btn_hint.configure(text=texts.get("hint", "Hint"))
        self.btn_undo.configure(text=texts.get("undo", "Undo"))
        self.btn_submit.configure(text=texts.get("submit", "Submit"))
        self.redraw()

    def export_to_pdf(self):
        import math
        import os
        import datetime
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.utils import ImageReader

        folder = "pdf"
        if not os.path.exists(folder): 
            os.makedirs(folder)
            
        # 🛡️ 1. ล้างตัวอักษรพิเศษออกจากชื่อไฟล์ ป้องกัน OSError จาก Emoji ในระบบปฏิบัติการ
        safe_name = "".join(char for char in self.player_name if char.isalnum() or char in "._- ").strip()
        if not safe_name:
            safe_name = "Player"
            
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Result_{safe_name}_{self.n}x{self.n}_{self.visual_style}_{timestamp}.pdf"
        filepath = os.path.join(folder, filename)

        # 📂 2. ระบบจัดการลงทะเบียนฟอนต์
        font_folder = "fonts"
        u_font = "Helvetica"  
        
        ttf_files = []
        if os.path.exists(font_folder):
            ttf_files = [f for f in os.listdir(font_folder) if f.lower().endswith('.ttf')]
            if ttf_files:
                main_font_file = ttf_files[0] 
                for f in ttf_files:
                    if "english" in f.lower():
                        main_font_file = f
                        break
                        
                try:
                    pdfmetrics.registerFont(TTFont("MainCustomFont", os.path.join(font_folder, main_font_file)))
                    u_font = "MainCustomFont"
                except Exception as e:
                    print(f"[PDF] Main Font Registration Error: {e}")

        def register_mode_font(font_name, keyword):
            if ttf_files:
                matched = [f for f in ttf_files if keyword.lower() in f.lower()]
                target_file = matched[0] if matched else ttf_files[0]
                try:
                    pdfmetrics.registerFont(TTFont(font_name, os.path.join(font_folder, target_file)))
                    return font_name
                except Exception as e:
                    print(f"ERROR: Could not register font {target_file}: {e}")
            return "Helvetica"

        thai_grid_font = register_mode_font("ThaiGridFont", "thai")
        japan_grid_font = register_mode_font("JapanGridFont", "japan")
        emoji_grid_font = register_mode_font("EmojiGridFont", "emoji")
        symbol_grid_font = register_mode_font("SymbolGridFont", "symbol")
        english_grid_font = register_mode_font("EnglishGridFont", "english")

        # 🎨 3. เริ่มสร้าง PDF และดีไซน์กรอบใบประกาศฯ
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4
        
        c.setFillColorRGB(0.96, 0.97, 0.99) 
        c.rect(0, 0, width, height, fill=1, stroke=0)

        bg_path = "images/background.jpg"
        if os.path.exists(bg_path):
            try: c.drawImage(bg_path, 0, 0, width=width, height=height)
            except: pass
            
        c.setFillColorRGB(1, 1, 1)
        c.roundRect(30, 30, width-60, height-60, 16, fill=1, stroke=0)
        
        c.setStrokeColorRGB(0.12, 0.23, 0.35) 
        c.setLineWidth(2.5)
        c.roundRect(36, 36, width-72, height-72, 12, fill=0, stroke=1)
        
        c.setStrokeColorRGB(0.85, 0.65, 0.25) 
        c.setLineWidth(1)
        c.roundRect(42, 42, width-84, height-84, 10, fill=0, stroke=1)

# 🛠️ 4. ฟังก์ชันอัจฉริยะในการวาดข้อความแบบผสมภาษา (Adaptive Text Renderer - ปรับปรุงเพื่อโหมด Emoji)
        def draw_mixed_text(canvas_obj, text, x, y, font_size, align="left", force_emoji_mode=False):
            segments = []
            for char in text:
                # 1. หากเปิดโหมด Emoji หรือเป็นตัวอักษร Emoji ให้บังคับใช้ฟอนต์ Emoji ทันที
                if force_emoji_mode or ord(char) > 0xffff or '\u2600' <= char <= '\u27bf' or '\u1f300' <= char <= '\u1f9ff':
                    f = emoji_grid_font
                # 2. ภาษาไทย
                elif '\u0e00' <= char <= '\u0e7f':
                    f = thai_grid_font
                # 3. ภาษาญี่ปุ่น
                elif '\u3040' <= char <= '\u30ff' or '\u4e00' <= char <= '\u9fff':
                    f = japan_grid_font
                # 4. สัญลักษณ์พิเศษ (เช่น ดาว, ลูกศร)
                elif ord(char) > 0x2000:
                    f = symbol_grid_font
                # 5. ภาษาอังกฤษและตัวเลขทั่วไป
                else:
                    f = english_grid_font
                segments.append((char, f))
            
            # คำนวณความกว้างรวมเพื่อรองรับ Alignment ป้องกันตัวหนังสือเบี้ยว
            total_width = 0
            for char, f in segments:
                try:
                    total_width += canvas_obj.stringWidth(char, f, font_size)
                except Exception:
                    total_width += canvas_obj.stringWidth("?", "Helvetica", font_size)
            
            current_x = x
            if align == "center":
                current_x = x - total_width / 2
            elif align == "right":
                current_x = x - total_width
                
            # วาดตัวอักษรทีละตัวลงบน Canvas
            for char, f in segments:
                try:
                    canvas_obj.setFont(f, font_size)
                    canvas_obj.drawString(current_x, y, char)
                    current_x += canvas_obj.stringWidth(char, f, font_size)
                except Exception:
                    # หากเกิดข้อผิดพลาด ให้ลองใช้ Helvetica สำรอง
                    try:
                        canvas_obj.setFont("Helvetica", font_size)
                        canvas_obj.drawString(current_x, y, "?")
                        current_x += canvas_obj.stringWidth("?", "Helvetica", font_size)
                    except Exception:
                        pass

        # 🏛️ 5. วาดส่วนหัวข้อความเกียรติบัตร (เรียกใช้ฟังก์ชันดึงตัวอักษรผสมป้องกันเครื่องหมาย ★ พัง)
        c.setFillColorRGB(0.12, 0.23, 0.35) 
        draw_mixed_text(c, "CONGRATULATIONS!", width/2, height-110, 30, align="center")
        
        c.setFillColorRGB(0.85, 0.62, 0.15) 
        draw_mixed_text(c, "★ Magic Square Master Completion Certificate ★", width/2, height-140, 15, align="center")

        # 📐 6. คำนวณพิกัดกระดาน (Grid Setup)
        grid_size = 280
        start_x = (width - grid_size) / 2
        start_y = (height - grid_size) / 2 + 15  
        cell_size = grid_size / self.n
        M = self.n * (self.n * self.n + 1) // 2

        c.setFillColorRGB(0.93, 0.95, 0.98)
        c.setStrokeColorRGB(0.75, 0.8, 0.85)
        c.setLineWidth(1.5)
        c.roundRect(start_x-10, start_y-10, grid_size+20, grid_size+20, 8, fill=1, stroke=1)

        # 🎯 7. แสดงผลรวมตัวเลขรอบกระดาน
        c.setFillColorRGB(0.15, 0.55, 0.25) 
        for i in range(self.n):
            rs = sum(self.current_nums[i])
            cs = sum(self.current_nums[r][i] for r in range(self.n))
            
            row_y_center = start_y + (self.n - 1 - i + 0.5) * cell_size
            draw_mixed_text(c, f"{rs}", start_x + grid_size + 15, row_y_center - 5, 14, align="left")
            
            col_x_center = start_x + (i + 0.5) * cell_size
            draw_mixed_text(c, f"{cs}", col_x_center, start_y + grid_size + 12, 14, align="center")
            
        diag1_sum = sum(self.current_nums[i][i] for i in range(self.n))
        c.setFillColorRGB(0.75, 0.15, 0.45) 
        draw_mixed_text(c, f"{diag1_sum} ↘", start_x - 15, start_y + grid_size + 12, 14, align="right")

        diag2_sum = sum(self.current_nums[i][self.n-1-i] for i in range(self.n))
        draw_mixed_text(c, f"↙ {diag2_sum}", start_x + grid_size + 15, start_y + grid_size + 12, 14, align="left")

        # 🧱 8. การวาดบล็อกแต่ละช่องและตัวอักษรในตาราง
        for r in range(self.n):
            for ci in range(self.n):
                x = start_x + ci * cell_size
                y = start_y + (self.n - 1 - r) * cell_size
                val = self.current_nums[r][ci]
                
                is_image_mode = (self.visual_style == "Creative" and val in self.image_pieces)
                
                if is_image_mode:
                    img_data = self.image_pieces[val]
                    c.drawImage(ImageReader(img_data), x + 1.5, y + 1.5, 
                                width=cell_size - 3, height=cell_size - 3, mask='auto')
                else:
                    if (r + ci) % 2 == 0: c.setFillColorRGB(0.99, 0.98, 0.93)
                    else: c.setFillColorRGB(0.94, 0.96, 0.99)
                    c.roundRect(x + 1.5, y + 1.5, cell_size - 3, cell_size - 3, 6, fill=1, stroke=0)
                
                c.setStrokeColorRGB(0.72, 0.78, 0.84)
                c.rect(x, y, cell_size, cell_size, fill=0, stroke=1)
                
                txt_col = (1, 1, 1) if is_image_mode else (0.15, 0.22, 0.35)
                c.setFillColorRGB(*txt_col)
                draw_mixed_text(c, str(val), x + cell_size * 0.15, y + cell_size * 0.85, int(cell_size * 0.15), align="center")
                
# (โค้ดส่วนอื่นคงเดิมในหัวข้อ 8 จนถึงจุดวาดตัวอักษรด้านล่าง)
                char = self.num_to_char.get(val, "")
                size_char = int(cell_size * 0.40)
                char_y_pos = y + cell_size * 0.30
                
                c.setFillColorRGB(0, 0, 0)
                
                # 🛠️ ส่งค่าตรวจสอบโหมดไปยัง Adaptive Renderer เพื่อเลือกฟอนต์ตามโหมดหลักได้แม่นยำขึ้น
                is_emoji_game = (self.mode == "Emoji")
                draw_mixed_text(c, str(char), x + cell_size/2, char_y_pos, size_char, align="center", force_emoji_mode=is_emoji_game)

        # 📊 9. การ์ดแผงสรุปสถิติด้านล่าง (Stats Panel)
        badge_y = 100
        badge_w, badge_h = 140, 52
        gap = 16
        start_badge_x = (width - (badge_w * 3 + gap * 2)) / 2
        
        stats_summary = [
            ("PLAYER NAME", self.player_name if self.player_name else "Guest", (0.85, 0.62, 0.15)),
            ("TOTAL MOVES", f"{self.move_count} Steps", (0.15, 0.55, 0.25)),
            ("GAME MODE", f"{self.mode}", (0.18, 0.45, 0.73))
        ]
        
        for idx, (label_title, value_desc, card_color) in enumerate(stats_summary):
            bx = start_badge_x + idx * (badge_w + gap)
            c.setFillColorRGB(0.97, 0.98, 0.99)
            c.roundRect(bx, badge_y, badge_w, badge_h, 6, fill=1, stroke=0)
            
            c.setFillColorRGB(*card_color)
            c.roundRect(bx, badge_y, 5, badge_h, 1.5, fill=1, stroke=0)
            
            c.setFillColorRGB(0.45, 0.5, 0.55)
            draw_mixed_text(c, label_title, bx + 15, badge_y + 35, 8, align="left")
            
            c.setFillColorRGB(0.15, 0.2, 0.25)
            # เรียกใช้ Adaptive Text Renderer กับชื่อผู้เล่นและข้อมูลสถิติทั้งหมดเพื่อความปลอดภัยสูงสุด
            draw_mixed_text(c, str(value_desc), bx + 15, badge_y + 14, 12, align="left")

        # 🕒 10. สรุปผลเวลาด้านขวาล่าง
        p_minutes = self.elapsed_time // 60
        p_seconds = self.elapsed_time % 60
        time_taken_str = f"{p_minutes:02d}:{p_seconds:02d}"
        completed_on_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        c.setFillColorRGB(0.5, 0.55, 0.6)
        draw_mixed_text(c, f"Time Elapsed: {time_taken_str}", width - 45, 70, 8, align="right")
        draw_mixed_text(c, f"Completed Date: {completed_on_str}", width - 45, 58, 8, align="right")
        
        c.save()

        # เปิดแสดงไฟล์ PDF ทันที
        from tkinter import messagebox
        try:
            if os.name == 'nt': os.startfile(filepath)
            else: os.system(f'open "{filepath}"')
        except: pass
        messagebox.showinfo("Export Success", f"บันทึกไฟล์เกียรติบัตรเรียบร้อยที่โฟลเดอร์ pdf:\n{filename}")

    def submit_game(self):
        n, M = self.n, self.n * (self.n * self.n + 1) // 2
        is_magic = (all(sum(r) == M for r in self.current_nums) and 
                    all(sum(self.current_nums[r][c] for r in range(n)) == M for c in range(n)) and
                    sum(self.current_nums[i][i] for i in range(n)) == M and
                    sum(self.current_nums[i][n-1-i] for i in range(n)) == M)
        if not is_magic:
            messagebox.showwarning("Result", "Magic Square not completed yet!")
            return
            
        # 👑 1. คำนวณระบบคะแนนตามที่วางแผนไว้
        base_scores = {3: 2000, 4: 5000, 5: 10000}
        base = base_scores.get(self.n, 2000)
        
        # ตัวคูณตามระดับความยากของทิศทางคำ
        pattern_multipliers = {
            "Horizontal": 1.0,
            "Vertical": 1.1,
            "Diagonal": 1.3,
            "Random All": 1.5
        }
        multiplier = pattern_multipliers.get(getattr(self, 'arrange_mode', 'Random All'), 1.5)
        
        # สูตรหักคะแนน Penalties
        calc_score = int((base * multiplier) - (self.elapsed_time * 2) - (self.move_count * 5) - (self.hint_count * 100))
        final_score = max(calc_score, 100) # บังคับขั้นต่ำให้ผู้เล่นได้ 100 คะแนน เผื่อเวลาติดลบเพื่อเป็นแรงใจสู้ต่อ
        
        # 📝 2. บันทึกข้อมูลลงฐานข้อมูลไฟล์ JSON
        json_file = "leaderboard.json"
        data = []
        if os.path.exists(json_file):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except:
                data = []
                
        # โครงสร้างตัวแปรเก็บสถิติ
        new_record = {
            "name": self.player_name if self.player_name else "Guest",
            "style": self.visual_style,       # "Standard" หรือ "Image" (Creative)
            "size": f"{self.n}x{self.n}",    # "3x3", "4x4", "5x5"
            "score": final_score,
            "time": self.elapsed_time,
            "moves": self.move_count,
            "pattern": getattr(self, 'arrange_mode', 'Random All'),
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        data.append(new_record)
        
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        # ทำกระบวนการส่งออกเกียรติบัตรตัวเดิมต่อ
        self.export_to_pdf() 
        self.on_finish()

    def update_timer(self):
        if self.timer_running and not self.game_won:
            self.elapsed_time = int(datetime.datetime.now().timestamp() - self.start_time)
            minutes = self.elapsed_time // 60
            seconds = self.elapsed_time % 60
            self.lbl_timer.configure(text=f"Time : {minutes:02d}:{seconds:02d}")
            self.card.after(1000, self.update_timer)

    def start_timer(self):
        self.start_time = datetime.datetime.now().timestamp()
        self.timer_running = True
        self.update_timer()

    def instant_win(self):
        self.current_nums = [row[:] for row in self.target_goal]
        self.move_count += 99  
        self.redraw()
        self.check_win_status()