# game_manager.py

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import random, os, datetime
import json

from logic import generate_magic_square, rotate_grid
from constants import get_fillers, LANG_DB, BTN_STYLES

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

        # =========================================================================
        # [โซนปรับแต่งความสวยงามเฉพาะโหมด Creative (โหมดเล่นแบบมีภาพพื้นหลัง)]
        # แก้ไขค่าวัดตรงนี้ได้เลยครับ ระบบจะอัปเดตทั้งหน้าจอเกมและใบเกียรติบัตรให้ตรงกัน
        # =========================================================================
        self.creative_img_opacity = 0.80      # ความชัดของรูปภาพ (0.0 = จางจนหาย, 1.0 = ชัดเท่าต้นฉบับ) ยิ่งจาง ฟอนต์ยิ่งเด่น
        self.creative_bg_blend = (255, 255, 255) # สีที่ใช้เกลี่ยผสมให้รูปจางลง (255, 255, 255 คือสีขาวช่วยให้ภาพดูคลีนสะอาด)
        self.creative_num_color = "#FFFFFF"   # สีของตัวเลข (แนะนำสีเข้มจัดหรือดำเพื่อให้ตัดกับรูปภาพจางๆ)
        self.creative_char_color = "#FFFFFF"  # สีของตัวอักษรปริศนา
        self.creative_border_color = "#D1D5DB" # สีเส้นขอบแบ่งช่องของโหมดรูปภาพ
        # =========================================================================
        
        self.top_bar = ctk.CTkFrame(self.card, fg_color="transparent")
        self.top_bar.pack(fill="x", pady=(20, 10), padx=30)

        self.btn_debug = ctk.CTkButton(self.top_bar, text="DEV", width=40, height=20, 
                                       command=self.instant_win, **BTN_STYLES["game_dev"])
        self.btn_debug.pack(side="right", padx=5)
        
        self.btn_back = ctk.CTkButton(self.top_bar, text="Cancel", width=90, height=35, 
                                      command=self.on_cancel, **BTN_STYLES["game_cancel"])
        self.btn_back.pack(side="left")

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
        self.arrange_mode = arrange_mode
        
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

                    # นวดเกลี่ยสีพื้นหลังตามระดับ Opacity เพื่อให้ภาพจางลงแบบมืออาชีพ สบายตาขึ้น
                    base_pastel = Image.new('RGBA', crop_img.size, self.creative_bg_blend + (255,))
                    final_piece = Image.blend(crop_img, base_pastel, alpha=1.0 - self.creative_img_opacity)

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
        if arrange in ["Horizontal", "Vertical", "Diagonal"]:
            path_coords = []
            n = self.n
            if arrange == "Horizontal":
                path_coords = [(r, c) for r in range(n) for c in range(n)]
            elif arrange == "Vertical":
                path_coords = [(r, c) for r in range(n) for c in range(n)]
            elif arrange == "Diagonal":
                for d in range(2 * n - 1):
                    for r in range(max(0, d - n + 1), min(n, d + 1)):
                        path_coords.append((r, d - r))
            
            flip_horizontal = random.choice([True, False])
            flip_vertical = random.choice([True, False])
            reverse_text = random.choice([True, False])
            
            transformed_coords = []
            for r, c in path_coords:
                new_r = (n - 1 - r) if flip_vertical else r
                new_c = (n - 1 - c) if flip_horizontal else c
                transformed_coords.append((new_r, new_c))
                
            if reverse_text:
                transformed_coords.reverse()
                        
            path_nums = [self.target_goal[r][c] for r, c in transformed_coords]
            self.num_to_char = {path_nums[i]: char_sequence[i] for i in range(n * n)}
        else:
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
                
                is_image_mode = (self.visual_style == "Creative" and val in self.image_pieces)
                
                if is_image_mode:
                    resized_img = self.image_pieces[val].resize((int(cell), int(cell)), Image.LANCZOS)
                    tk_img = ImageTk.PhotoImage(resized_img)
                    self.tk_images.append(tk_img)
                    self.canvas.create_image(x, y, anchor="nw", image=tk_img)
                    self.canvas.create_rectangle(x, y, x+cell, y+cell, outline=self.creative_border_color, width=1)
                    
                    # เรียกใช้ชุดสีเฉพาะของ Creative จากคอนฟิกด้านบน
                    num_color = self.creative_num_color
                    char_color = self.creative_char_color
                else:
                    # ส่วนของโหมด Standard (ไม่เปลี่ยนแปลงใดๆ ทั้งสิ้นเพื่อคุมโทนเดิม)
                    bg_colors = ["#EBF5FB", "#FEF9E7", "#EAFAF1", "#F4ECF7"]
                    base_bg = bg_colors[(r + c) % len(bg_colors)]
                    bg = base_bg if (r, c) != self.selected else "#FBEEE6"
                    self.canvas.create_rectangle(x, y, x+cell, y+cell, fill=bg, outline="#AEB6BF", width=1)
                    
                    num_color = "#2E4053"
                    char_color = "#2E4053"
                
                if (r, c) == self.selected:
                    self.canvas.create_rectangle(x, y, x+cell, y+cell, outline="#FF7676", width=4)
                
                char_font_family = "Garamond"
                if char:
                    o = ord(char)
                    if 0x2000 <= o <= 0x2BFF or char in "★☆◎◇◆○●▲▼■□☯⛩♪♬♻⛶⚦⚨⚔⚒⛭🕇↘↙↖↗♠♣♥♦♔♕♖♗♘♙⚙⚓⚖":
                        char_font_family = "Segoe UI Symbol"
                    elif o > 0xffff or char in ["🌟", "🚀", "🎈", "🍎", "🍊", "🍇", "🐶", "🐱", "⚽", "🏀", "🎨", "🎬", "🎸", "🍕", "🍦", "🛸"]:
                        char_font_family = "Segoe UI Emoji"
                    elif '\u3040' <= char <= '\u30ff' or '\u4e00' <= char <= '\u9fff':
                        char_font_family = "MS Gothic"
                    elif '\u0e00' <= char <= '\u0e7f':
                        char_font_family = "Tahoma"

                num_font = ("Garamond", int(cell * 0.15), "bold")
                char_font = (char_font_family, int(cell * 0.45), "bold")
                
                num_y = y + cell * 0.2
                char_y = y + cell * 0.55

                self.canvas.create_text(x + cell/2, num_y, text=str(val), font=num_font, fill=num_color)
                self.canvas.create_text(x + cell/2, char_y, text=char, font=char_font, fill=char_color)

        row_sums = [sum(row) for row in self.current_nums]
        col_sums = [sum(self.current_nums[r][ci] for r in range(n)) for ci in range(n)]
        diag1_sum = sum(self.current_nums[i][i] for i in range(n))       
        diag2_sum = sum(self.current_nums[i][n-1-i] for i in range(n))   

        for i in range(n):
            self.canvas.create_text(x0 + n*cell + 25, y0 + i*cell + cell/2, text=str(row_sums[i]), fill=("#27AE60" if row_sums[i] == M else "#E74C3C"), font=("Garamond", 14, "bold"))
            self.canvas.create_text(x0 + i*cell + cell/2, y0 - 25, text=str(col_sums[i]), fill=("#27AE60" if col_sums[i] == M else "#E74C3C"), font=("Garamond", 14, "bold"))
        self.canvas.create_text(x0 - 35, y0 - 25, text=f"{diag1_sum} ↘", fill=("#27AE60" if diag1_sum == M else "#E74C3C"), font=("Segoe UI Symbol", 14, "bold"))
        self.canvas.create_text(x0 + n*cell + 35, y0 - 25, text=f"↙ {diag2_sum}", fill=("#27AE60" if diag2_sum == M else "#E74C3C"), font=("Segoe UI Symbol", 14, "bold"))
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

    def export_to_image(self):
        folder = "certificates"
        if not os.path.exists(folder): 
            os.makedirs(folder)
            
        # [ปรับปรุงเพื่อรองรับทุกภาษา] กรองเฉพาะตัวอักษรที่ระบบปฏิบัติการห้ามใช้ในชื่อไฟล์ออกเท่านั้น
        # วิธีนี้จะทำให้ชื่อภาษาไทย ญี่ปุ่น อังกฤษ หรือช่องว่าง คงอยู่ครบถ้วนอย่างปลอดภัย
        forbidden_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
        safe_name = "".join(char for char in self.player_name if char not in forbidden_chars).strip()
        if not safe_name: 
            safe_name = "Player"
            
        # แยกข้อมูลวันที่และเวลาออกจากกันตามแพทเทิร์นที่กำหนด
        now = datetime.datetime.now()
        date_str = now.strftime("%Y%m%d")  # รูปแบบ: ปีเดือนวัน (เช่น 20260528)
        time_str = now.strftime("%H%M%S")  # รูปแบบ: ชั่วโมงนาทีวินาที (เช่น 131530)
        
        # [ปรับปรุง] ตั้งชื่อไฟล์ตามแพทเทิร์น: Certificate_{Name}_{Size}_{Mode}_{Date}_{Time}.png
        filename = f"Certificate_{safe_name}_{self.n}x{self.n}_{self.mode}_{date_str}_{time_str}.png"
        filepath = os.path.join(folder, filename)

        img_w, img_h = 1240, 1754
        cert_img = Image.new("RGBA", (img_w, img_h), (255, 255, 255, 255))
        draw = ImageDraw.Draw(cert_img)

        # วาดพื้นหลัง Gradient ไล่โทนสุภาพเรียบร้อย
        for y in range(img_h):
            ratio = y / img_h
            r_c = int(30 + ratio * 40)
            g_c = int(30 + ratio * 20)
            b_c = int(45 + ratio * 30)
            draw.line([(0, y), (img_w, y)], fill=(r_c, g_c, b_c, 255))

        # กรอบการ์ดสีขาวหลัก
        card_margin = 50
        draw.rounded_rectangle([card_margin, card_margin, img_w - card_margin, img_h - card_margin], radius=25, fill=(255, 255, 255, 255))
        draw.rounded_rectangle([card_margin + 10, card_margin + 10, img_w - card_margin - 10, img_h - card_margin - 10], radius=20, outline=(30, 50, 80, 255), width=4)

        def load_font(font_key, size):
            font_paths = {
                "emoji": ["C:\\Windows\\Fonts\\seguiemj.ttf", "/System/Library/Fonts/Apple Color Emoji.ttc", "NotoColorEmoji.ttf", "tahoma.ttf"],
                "symbol": ["C:\\Windows\\Fonts\\seguisym.ttf", "C:\\Windows\\Fonts\\msgothic.ttc", "/System/Library/Fonts/Supplemental/Apple Symbols.ttf", "tahoma.ttf"],
                "thai": ["C:\\Windows\\Fonts\\tahoma.ttf", "C:\\Windows\\Fonts\\cordia.ttf", "/System/Library/Fonts/Supplemental/Tahoma.ttf"],
                "japan": ["C:\\Windows\\Fonts\\msgothic.ttc", "/System/Library/Fonts/Supplemental/MS Gothic.ttc"],
                "english": ["C:\\Windows\\Fonts\\georgiab.ttf", "C:\\Windows\\Fonts\\Garamond.ttf", "arial.ttf"]
            }
            for path in font_paths.get(font_key, []):
                if os.path.exists(path):
                    try: return ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.BASIC)
                    except:
                        try: return ImageFont.truetype(path, size)
                        except: pass
            return ImageFont.load_default()

        def draw_mixed_text(text_str, x, y, size, fill_color, anchor="mm"):
            fonts_map = {
                "english": load_font("english", size),
                "thai": load_font("thai", size),
                "japan": load_font("japan", size),
                "symbol": load_font("symbol", size),
                "emoji": load_font("emoji", size)
            }
            
            char_data = []
            total_w = 0
            for ch in text_str:
                o = ord(ch)
                if 0x0E00 <= o <= 0x0E7F:
                    ftype = "thai"
                elif 0x3040 <= o <= 0x30FF or 0x4E00 <= o <= 0x9FFF or 0xFF00 <= o <= 0xFFEF:
                    ftype = "japan"
                elif 0x2000 <= o <= 0x2BFF or ch in "★☆◎◇◆○●▲▼■□☯⛩♪♬♻⛶⚦⚨⚔⚒⛭🕇↘↙↖↗♠♣♥♦♔♕♖♗♘♙⚙⚓⚖":
                    ftype = "symbol"
                elif o > 0xFFFF:
                    ftype = "emoji"
                else:
                    ftype = "english"
                
                f = fonts_map[ftype]
                try: w = draw.textlength(ch, font=f)
                except: w = f.getbbox(ch)[2] - f.getbbox(ch)[0] if hasattr(f, "getbbox") else 12
                
                char_data.append((ch, f, w))
                total_w += w
            
            if anchor == "mm":
                curr_x = x - total_w / 2
            elif anchor == "rm":
                curr_x = x - total_w
            else:
                curr_x = x

            for ch, f, w in char_data:
                draw.text((curr_x, y), ch, font=f, fill=fill_color, anchor="lm")
                curr_x += w

            return total_w

        # หัวข้อใบเซอร์ด้านบน
        draw_mixed_text("CONGRATULATIONS!", img_w / 2, 200, 64, (30, 50, 80, 255), anchor="mm")
        draw_mixed_text("Magic Square Master Completion Certificate", img_w / 2, 270, 28, (194, 130, 12, 255), anchor="mm")

        # ตารางปริศนา
        grid_size = 580
        start_x = (img_w - grid_size) / 2
        start_y = 420  
        cell_size = grid_size / self.n
        M = self.n * (self.n * self.n + 1) // 2

        # พื้นหลังแผงตารางปริศนา
        draw.rounded_rectangle([start_x - 15, start_y - 15, start_x + grid_size + 15, start_y + grid_size + 15], radius=12, fill=(244, 246, 249, 255), outline=(210, 218, 226, 255), width=2)

        # วาดผลรวมแนวตั้งและแนวนอนรอบตาราง
        for i in range(self.n):
            rs = sum(self.current_nums[i])
            cs = sum(self.current_nums[r][i] for r in range(self.n))
            draw_mixed_text(str(rs), start_x + grid_size + 50, start_y + (i + 0.5) * cell_size, 24, (39, 174, 96, 255) if rs == M else (231, 76, 60, 255), anchor="mm")
            draw_mixed_text(str(cs), start_x + (i + 0.5) * cell_size, start_y - 45, 24, (39, 174, 96, 255) if cs == M else (231, 76, 60, 255), anchor="mm")

        diag1_sum = sum(self.current_nums[i][i] for i in range(self.n))
        diag2_sum = sum(self.current_nums[i][self.n - 1 - i] for i in range(self.n))
        
        draw_mixed_text(f"{diag1_sum} ↘", start_x - 60, start_y - 45, 24, (39, 174, 96, 255) if diag1_sum == M else (231, 76, 60, 255), anchor="mm")
        draw_mixed_text(f"↙ {diag2_sum}", start_x + grid_size + 60, start_y - 45, 24, (39, 174, 96, 255) if diag2_sum == M else (231, 76, 60, 255), anchor="mm")

        bg_colors_hex = ["#EBF5FB", "#FEF9E7", "#EAFAF1", "#F4ECF7"]
        def hex_to_rgb(hex_str):
            h = hex_str.lstrip('#')
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (255,)

        # ลูปวาดช่องในตาราง
        for r in range(self.n):
            for ci in range(self.n):
                x_pos = start_x + ci * cell_size
                y_pos = start_y + r * cell_size
                val = self.current_nums[r][ci]
                char = self.num_to_char.get(val, "")
                
                is_image_mode = (self.visual_style == "Creative" and val in self.image_pieces)
                
                if is_image_mode:
                    piece_img = self.image_pieces[val].resize((int(cell_size - 4), int(cell_size - 4)), Image.LANCZOS)
                    cert_img.paste(piece_img, (int(x_pos + 2), int(y_pos + 2)), piece_img if piece_img.mode == "RGBA" else None)
                    num_col = hex_to_rgb(self.creative_num_color)
                    char_col = hex_to_rgb(self.creative_char_color)
                else:
                    bg_color_pick = bg_colors_hex[(r + ci) % len(bg_colors_hex)]
                    bg_cell_color = hex_to_rgb(bg_color_pick)
                    draw.rectangle([x_pos + 2, y_pos + 2, x_pos + cell_size - 2, y_pos + cell_size - 2], fill=bg_cell_color)
                    num_col = (46, 64, 83, 255)
                    char_col = (46, 64, 83, 255)

                draw.rectangle([x_pos, y_pos, x_pos + cell_size, y_pos + cell_size], outline=(174, 182, 191, 255), width=1)

                num_y_offset = y_pos + cell_size * 0.22
                char_y_offset = y_pos + cell_size * 0.60
                
                draw_mixed_text(str(val), x_pos + cell_size / 2, num_y_offset, int(cell_size * 0.15), num_col, anchor="mm")
                draw_mixed_text(str(char), x_pos + cell_size / 2, char_y_offset, int(cell_size * 0.44), char_col, anchor="mm")

        # แผงข้อมูลผู้เล่นด้านล่าง
        badge_y = 1260  
        badge_w, badge_h = 320, 115
        badge_gap = 40
        start_badge_x = (img_w - (badge_w * 3 + badge_gap * 2)) / 2

        stats_summary = [
            ("PLAYER NAME", self.player_name if self.player_name else "Guest", (194, 130, 12, 255)),
            ("TOTAL MOVES", f"{self.move_count} Steps", (39, 174, 96, 255)),
            ("GAME MODE", f"{self.mode}", (41, 128, 185, 255))
        ]

        for idx, (title, desc, color_theme) in enumerate(stats_summary):
            bx = start_badge_x + idx * (badge_w + badge_gap)
            draw.rounded_rectangle([bx, badge_y, bx + badge_w, badge_y + badge_h], radius=12, fill=(248, 249, 250, 255))
            draw.rounded_rectangle([bx, badge_y, bx + 12, badge_y + badge_h], radius=4, fill=color_theme)
            
            draw_mixed_text(title, bx + 35, badge_y + 35, 20, (100, 110, 120, 255), anchor="lm")
            draw_mixed_text(desc, bx + 35, badge_y + 78, 25, (30, 30, 30, 255), anchor="lm")

        p_minutes = self.elapsed_time // 60
        p_seconds = self.elapsed_time % 60
        time_taken_str = f"{p_minutes:02d}:{p_seconds:02d}"
        completed_on_str = now.strftime("%Y-%m-%d %H:%M:%S")

        # วันที่และเวลาขวาล่างสุด
        draw_mixed_text(f"Time Elapsed: {time_taken_str}", img_w - 90, 1580, 16, (120, 130, 140, 255), anchor="rm")
        draw_mixed_text(f"Completed Date: {completed_on_str}", img_w - 90, 1615, 16, (120, 130, 140, 255), anchor="rm")
    
        final_cert = cert_img.convert("RGB")
        final_cert.save(filepath, "PNG")

        try:
            if os.name == 'nt': os.startfile(filepath)
            else: os.system(f'open "{filepath}"')
        except: pass
        
        texts = LANG_DB.get(self.get_lang(), LANG_DB["English"])
        messagebox.showinfo(texts["cert_success_title"], f"{texts['cert_success_msg']}\n{filename}")

    def submit_game(self):
        n, M = self.n, self.n * (self.n * self.n + 1) // 2
        is_magic = (all(sum(r) == M for r in self.current_nums) and 
                    all(sum(self.current_nums[r][c] for r in range(n)) == M for c in range(n)) and
                    sum(self.current_nums[i][i] for i in range(n)) == M and
                    sum(self.current_nums[i][n-1-i] for i in range(n)) == M)
        if not is_magic:
            messagebox.showwarning("Result", "Magic Square not completed yet!")
            return

        pattern_base_scores = {
            "Horizontal": 15000, "Vertical": 15000, "Diagonal": 22500, "Random All": 30000
        }
        target_pattern = getattr(self, 'arrange_mode', "Random All")
        base_score = pattern_base_scores.get(target_pattern, 30000)
        penalty = (self.elapsed_time * 2) + (self.move_count * 5) + (self.hint_count * 100)
        final_score = max(base_score - penalty, 100)
        
        target_style = "Creative" if self.visual_style == "Image" else "Standard"
        json_file = "leaderboard.json"
        data = []
        if os.path.exists(json_file):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except: data = []
                
        player_name = self.player_name if self.player_name else "Guest"
        target_size = f"{self.n}x{self.n}"
        
        found = False
        for item in data:
            if (item.get("name") == player_name and 
                item.get("style") == target_style and 
                item.get("size") == target_size and 
                item.get("pattern") == target_pattern and
                item.get("mode") == self.mode):
                found = True
                if final_score > item.get("score", 0):
                    item.update({
                        "score": final_score,
                        "time": self.elapsed_time,
                        "moves": self.move_count,
                        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                break 
                
        if not found:
            new_record = {
                "name": player_name,
                "style": target_style,
                "size": target_size,
                "pattern": target_pattern,
                "mode": self.mode,
                "score": final_score,
                "time": self.elapsed_time,
                "moves": self.move_count,
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            data.append(new_record)
            
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        self.export_to_image() 
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
        self.move_count = 99  
        self.redraw()
        self.check_win_status()