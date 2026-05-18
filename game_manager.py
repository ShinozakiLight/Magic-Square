# game_manager.py (Updated for Classic Mode & Better PDF)

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
from constants import get_fillers
from constants import LANG_DB

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
        self.visual_style = "Image" # เพิ่มตัวแปรเช็คโหมด Visual
        
        self.top_bar = ctk.CTkFrame(self.card, fg_color="transparent")
        self.top_bar.pack(fill="x", pady=(20, 10), padx=30)

        self.btn_debug = ctk.CTkButton(self.top_bar, text="DEV", width=40, height=20, 
                                       font=("Arial", 10), command=self.instant_win, 
                                       fg_color="#333333", text_color="yellow", 
                                       hover_color="#555555")
        self.btn_debug.pack(side="right", padx=5)
        
        self.btn_back = ctk.CTkButton(self.top_bar, text="Cancel", width=90, height=35, 
                                      font=("Garamond", 16), command=self.on_cancel, 
                                      fg_color="#B3B3B3", text_color="white", 
                                      border_color="black", border_width=1, corner_radius=0)
        self.btn_back.pack(side="left")

        self.btn_shuffle = ctk.CTkButton(self.top_bar, text="Shuffle", width=90, height=35, 
                                         font=("Garamond", 16), command=self.shuffle_board, 
                                         fg_color="#FF7676", text_color="white", 
                                         border_color="black", border_width=1, corner_radius=0)
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
        
        btn_style = {"width": 130, "height": 40, "font": ("Garamond", 18), "text_color": "white", 
                     "border_color": "black", "border_width": 1, "corner_radius": 0}

        self.btn_hint = ctk.CTkButton(self.bottom_bar, text="Hint", command=self.give_hint, 
                                      fg_color="#27AE60", **btn_style)
        self.btn_hint.pack(side="left", padx=20, expand=True)

        self.btn_undo = ctk.CTkButton(self.bottom_bar, text="Undo", command=self.undo, 
                                      fg_color="#8C8CB3", **btn_style)
        self.btn_undo.pack(side="left", padx=20, expand=True)

        self.btn_submit = ctk.CTkButton(self.bottom_bar, text="Submit", command=self.submit_game, 
                                        fg_color="#85C1E9", **btn_style)
        self.btn_submit.pack(side="left", padx=20, expand=True)

    def start_new_game(self, name, size, mode, image_path):
        self.player_name = name
        self.n = size
        self.mode = mode
        self.visual_style = "Image" if image_path else "Classic"
        self.rotation_k = random.randint(0, 3)
        self.move_count = 0
        self.hint_count = 0 
        self.undo_stack.clear()
        self.selected = None
        self.image_pieces = {}
        self.win_status_label.configure(text="")
        self.game_won = False 
        self.elapsed_time = 0
        self.start_timer()

        M = self.n * (self.n * self.n + 1) // 2
        self.lbl_target.configure(text=f"Target : {M}")
        
        self.rebuild_mapping(name, mode)
        if image_path:
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
                    overlay = Image.new('RGBA', crop_img.size, (255, 255, 255, 30))
                    final_piece = Image.alpha_composite(crop_img, overlay)
                    target_num = self.target_goal[r][c]
                    self.image_pieces[target_num] = final_piece
        except Exception as e:
            print(f"Error loading image: {e}")

    def rebuild_mapping(self, name, mode):
        # 1. สร้างตารางคำตอบที่เป็นตัวเลข (Logic เดิม)
        base_target = generate_magic_square(self.n)
        self.target_goal = rotate_grid(base_target, self.rotation_k)
        
        # 2. เตรียมตัวอักษรชื่อ + ตัวเติมให้ครบจำนวนช่อง (เช่น 9 ช่อง)
        fillers = get_fillers(mode)
        name_chars = list(name.upper()) if name else []
        char_sequence = name_chars
        idx = 0
        while len(char_sequence) < self.n * self.n:
            char_sequence.append(fillers[idx % len(fillers)])
            idx += 1

        # 3. สร้างลิสต์ตัวเลข 1 ถึง n^2 แล้ว "สุ่มลำดับ" (Shuffle)
        # วิธีนี้จะทำให้ตัวอักษรแต่ละตัวไปคู่กับเลขแบบสุ่ม ไม่เรียงตามชื่อ
        all_nums = list(range(1, self.n * self.n + 1))
        random.shuffle(all_nums) 
        
        # 4. จับคู่ Mapping ใหม่
        # ตัวอักษรตัวที่ 1 (K) อาจไปคู่กับเลข 5, ตัวที่ 2 (A) อาจไปคู่กับเลข 1
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

                if self.visual_style == "Image" and val in self.image_pieces:
                    resized_img = self.image_pieces[val].resize((int(cell), int(cell)), Image.LANCZOS)
                    tk_img = ImageTk.PhotoImage(resized_img)
                    self.tk_images.append(tk_img)
                    self.canvas.create_image(x, y, anchor="nw", image=tk_img)
                    text_color = "white"
                    outline_color = "#CCCCCC"
                else:
                    # Classic Mode: ใช้สีพาสเทลสลับกันเพื่อให้ดูมีมิติ
                    bg_colors = ["#EBF5FB", "#FEF9E7", "#EAFAF1", "#F4ECF7"]
                    base_bg = bg_colors[(r + c) % len(bg_colors)]
                    bg = base_bg if (r, c) != self.selected else "#FBEEE6"
                    self.canvas.create_rectangle(x, y, x+cell, y+cell, fill=bg, outline="#AEB6BF", width=1)
                    text_color = "#2E4053"
                    outline_color = "#AEB6BF"
                
                if (r, c) == self.selected:
                    self.canvas.create_rectangle(x, y, x+cell, y+cell, outline="#FF7676", width=4)
                
                self.canvas.create_text(x+cell/2, y+cell*0.2, text=str(val), 
                                        font=("Garamond", int(cell*0.15), "bold"), fill=text_color)
                self.canvas.create_text(x+cell/2, y+cell*0.6, text=char, 
                                        font=("Garamond", int(cell*0.45), "bold"), fill=text_color)

        # Sums Calculation
        row_sums = [sum(row) for row in self.current_nums]
        col_sums = [sum(self.current_nums[r][ci] for r in range(n)) for ci in range(n)]
        diag1_sum = sum(self.current_nums[i][i] for i in range(n))       
        diag2_sum = sum(self.current_nums[i][n-1-i] for i in range(n))   

        for i in range(n):
            self.canvas.create_text(x0 + n*cell + 25, y0 + i*cell + cell/2, text=str(row_sums[i]), 
                                    fill=("#27AE60" if row_sums[i] == M else "#E74C3C"), font=("Garamond", 14, "bold"))
            self.canvas.create_text(x0 + i*cell + cell/2, y0 - 25, text=str(col_sums[i]), 
                                    fill=("#27AE60" if col_sums[i] == M else "#E74C3C"), font=("Garamond", 14, "bold"))
        
        self.canvas.create_text(x0 - 35, y0 - 25, text=f"{diag1_sum} ↘", 
                                fill=("#27AE60" if diag1_sum == M else "#E74C3C"), font=("Garamond", 14, "bold"))
        self.canvas.create_text(x0 + n*cell + 35, y0 - 25, text=f"↙ {diag2_sum}", 
                                fill=("#27AE60" if diag2_sum == M else "#E74C3C"), font=("Garamond", 14, "bold"))
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
        wrong_positions = [(r, c) for r in range(self.n) for c in range(self.n) 
                       if self.current_nums[r][c] != self.target_goal[r][c]]
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
        """อัปเดตตัวหนังสือบน UI ของ GameManager เมื่อมีการเปลี่ยนภาษา"""
        texts = LANG_DB[self.get_lang()]
        
        # อัปเดตปุ่มต่างๆ
        self.btn_back.configure(text=texts.get("cancel", "Cancel"))
        self.btn_shuffle.configure(text=texts.get("shuffle", "Shuffle"))
        self.btn_hint.configure(text=texts.get("hint", "Hint"))
        self.btn_undo.configure(text=texts.get("undo", "Undo"))
        self.btn_submit.configure(text=texts.get("submit", "Submit"))
        
        # สั่งวาด Canvas ใหม่เพื่ออัปเดตข้อความ Moves และ Target ในตาราง
        self.redraw()

    def export_to_pdf(self):
        folder = "pdf"
        if not os.path.exists(folder): 
            os.makedirs(folder)
            
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Result_{self.player_name}_{self.n}x{self.n}_{self.visual_style}_{timestamp}.pdf"
        filepath = os.path.join(folder, filename)
        
        # --- 1. เตรียมระบบ Font ---
        font_header = "Helvetica-Bold" 
        font_footer = "Helvetica"
        
        # ค้นหา Font พิเศษสำหรับตัวอักษรในตาราง (Grid) เท่านั้น
        search_paths = {
            "Thai": ["fonts/NotoSansThai-Regular.ttf", "C:/Windows/Fonts/tahoma.ttf"],
            "Japanese": ["fonts/NotoSansJP-Regular.ttf", "C:/Windows/Fonts/msgothic.ttc"],
            "English": ["fonts/Garamond.ttf", "C:/Windows/Fonts/gara.ttf", "C:/Windows/Fonts/arial.ttf"]
        }
        
        def try_register(alias, paths):
            for p in paths:
                if os.path.exists(p):
                    try: 
                        pdfmetrics.registerFont(TTFont(alias, p, subfontIndex=0 if p.lower().endswith(".ttc") else -1))
                        return alias
                    except: continue
            return "Helvetica-Bold" # Fallback ถ้าไม่เจอไฟล์ฟอนต์เลย

        # ลงทะเบียนฟอนต์สำหรับตาราง
        grid_font = try_register("GridFont", search_paths.get(self.mode, search_paths["English"]))

        # --- 2. เริ่มสร้าง Canvas ---
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4

        # วาด Background (ถ้ามี)
        bg_path = "images/background.jpg"
        if os.path.exists(bg_path):
            try: c.drawImage(bg_path, 0, 0, width=width, height=height)
            except: pass

        # วาดแผ่นกระดาษขาวซ้อนทับ
        c.setFillColorRGB(1, 1, 1)
        c.rect(50, 50, width-100, height-100, fill=1, stroke=0)

        # --- 3. ส่วนหัว (ใช้ Font มาตรฐาน) ---
        c.setFillColorRGB(0, 0, 0)
        c.setFont(font_header, 30) 
        c.drawCentredString(width/2, height-140, "Congratulations!")
        c.setFont(font_footer, 16)
        c.drawCentredString(width/2, height-170, "Magic Square Masterpiece")

        # กำหนดขนาดตาราง
        grid_size = 300
        start_x, start_y = (width-grid_size)/2, height-520
        cell_size = grid_size / self.n
        M = self.n * (self.n * self.n + 1) // 2

        # --- 4. วาดผลรวมรอบตาราง (ใช้ Font มาตรฐาน) ---
        c.setFont(font_header, 12)
        c.setFillColorRGB(0.1, 0.5, 0.3) # สีเขียวเข้ม
        for i in range(self.n):
            rs = sum(self.current_nums[i])
            cs = sum(self.current_nums[r][i] for r in range(self.n))
            # ผลรวมแถว (ขวา)
            c.drawString(start_x + grid_size + 15, start_y + (self.n-1-i+0.35)*cell_size, str(rs))
            # ผลรวมหลัก (บน)
            c.drawCentredString(start_x + (i+0.5)*cell_size, start_y + grid_size + 10, str(cs))

        # --- 5. วาดตารางและตัวอักษร ---
        for r in range(self.n):
            for ci in range(self.n):
                x, y = start_x + ci*cell_size, start_y + (self.n-1-r)*cell_size
                val = self.current_nums[r][ci]
                char = self.num_to_char.get(val, "")

                if self.visual_style == "Image" and val in self.image_pieces:
                    # โหมดรูปภาพ
                    try: 
                        c.drawImage(ImageReader(self.image_pieces[val]), x, y, width=cell_size, height=cell_size)
                    except: pass
                    txt_col = (1, 1, 1) # ตัวอักษรสีขาวบนรูป
                else:
                    # โหมด Classic (สลับสีช่อง)
                    if (r + ci) % 2 == 0:
                        c.setFillColorRGB(0.95, 0.96, 1.0) # สีฟ้าอ่อน
                    else:
                        c.setFillColorRGB(0.92, 0.93, 0.95) # สีเทาอ่อน
                    c.rect(x, y, cell_size, cell_size, fill=1, stroke=0)
                    txt_col = (0.1, 0.2, 0.3) # ตัวอักษรสีน้ำเงินเข้ม

                # วาดเส้นขอบช่อง
                c.setStrokeColorRGB(0.7, 0.7, 0.7)
                c.rect(x, y, cell_size, cell_size, fill=0, stroke=1)

                # วาดเลขลำดับเล็กๆ (ใช้ Font มาตรฐาน)
                c.setFillColorRGB(*txt_col)
                c.setFont(font_footer, 8)
                c.drawString(x + 5, y + cell_size - 12, str(val))

                # วาดตัวอักษรหลัก (ใช้ grid_font ตามโหมดภาษา)
                c.setFont(grid_font, 28)
                c.drawCentredString(x + cell_size/2, y + cell_size/2 - 10, char)

        # --- 6. ส่วนท้าย (ใช้ Font มาตรฐาน) ---
        c.setFillColorRGB(0, 0, 0)
        c.setFont(font_header, 14)
        c.drawCentredString(width/2, 180, f"Player: {self.player_name}  |  Score: {self.move_count} moves")
        c.setFont(font_footer, 10)
        c.drawCentredString(width/2, 150, f"Mode: {self.mode} ({self.visual_style}) - {timestamp}")
        
        c.save()

        # เปิดไฟล์อัตโนมัติ
        try:
            if os.name == 'nt': os.startfile(filepath)
            else: os.system(f'open "{filepath}"')
        except: pass
        
        messagebox.showinfo("Export Success", f"บันทึกไฟล์เรียบร้อยที่:\n{filename}")

    def submit_game(self):
        n, M = self.n, self.n * (self.n * self.n + 1) // 2
        is_magic = (all(sum(r) == M for r in self.current_nums) and 
                    all(sum(self.current_nums[r][c] for r in range(n)) == M for c in range(n)) and
                    sum(self.current_nums[i][i] for i in range(n)) == M and
                    sum(self.current_nums[i][n-1-i] for i in range(n)) == M)
        if not is_magic:
            messagebox.showwarning("Result", "Magic Square not completed yet!")
            return
        self.export_to_pdf() 
        self.on_finish()

    def update_timer(self):
        if self.timer_running and not self.game_won:
            self.elapsed_time = int(datetime.datetime.now().timestamp() - self.start_time)
            minutes = self.elapsed_time // 60
            seconds = self.elapsed_time % 60
            self.lbl_timer.configure(text=f"Time : {minutes:02d}:{seconds:02d}")
            # สั่งให้รันฟังก์ชันนี้ซ้ำทุกๆ 1 วินาที (1000 ms)
            self.card.after(1000, self.update_timer)

    def start_timer(self):
        self.start_time = datetime.datetime.now().timestamp()
        self.timer_running = True
        self.update_timer()

    def instant_win(self):
        # ก็อปปี้ตารางเฉลยมาใส่ในกระดานปัจจุบันทันที
        self.current_nums = [row[:] for row in self.target_goal]
        self.move_count += 99  # ให้รู้ว่าใช้ทางลัด
        self.redraw()
        # เรียกเช็คชัยชนะทันที
        self.check_win_status()