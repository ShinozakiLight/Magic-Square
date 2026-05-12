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

class GameManager:
    def __init__(self, master_card, on_cancel_callback, on_finish_callback):
        self.card = master_card
        self.on_cancel = on_cancel_callback
        self.on_finish = on_finish_callback
        
        self.n = 3
        self.move_count = 0
        self.hint_count = 0  
        self.selected = None
        self.undo_stack = []
        self.image_pieces = {}
        self.tk_images = []
        self.mode = "English" # เก็บสถานะโหมดไว้ใช้ตอนพริ้นท์
        
        self.top_bar = ctk.CTkFrame(self.card, fg_color="transparent")
        self.top_bar.pack(fill="x", pady=(20, 10), padx=30)
        
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

        self.canvas = tk.Canvas(self.card, bg="white", highlightthickness=0, borderwidth=0, bd=0)
        self.canvas.pack(fill="both", expand=True, padx=40, pady=5)
        self.canvas.bind("<Button-1>", self.on_click)

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
        self.rotation_k = random.randint(0, 3)
        self.move_count = 0
        self.hint_count = 0 
        self.undo_stack.clear()
        self.selected = None
        self.image_pieces = {}
        self.win_status_label.configure(text="")
        
        self.game_won = False 

        M = self.n * (self.n * self.n + 1) // 2
        self.lbl_target.configure(text=f"Target : {M}")
        
        self.rebuild_mapping(name, mode)
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
        base_target = generate_magic_square(self.n)
        self.target_goal = rotate_grid(base_target, self.rotation_k)
        flat_goal = [num for row in self.target_goal for num in row]
        fillers = get_fillers(mode)
        name_chars = list(name.upper()) if name else []
        char_sequence = name_chars
        idx = 0
        while len(char_sequence) < self.n * self.n:
            char_sequence.append(fillers[idx % len(fillers)])
            idx += 1
        self.num_to_char = {num: char_sequence[i] for i, num in enumerate(flat_goal)}

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
        if getattr(self, 'game_won', False):
            return 
            
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
        self.canvas.delete("all")
        self.canvas.update_idletasks() 
        W, H = self.canvas.winfo_width(), self.canvas.winfo_height()
        if W < 10: W, H = 550, 450
        
        n, cell = self.n, min((W - 100) / self.n, (H - 100) / self.n)
        x0, y0 = (W - n * cell) / 2, (H - n * cell) / 2
        self.layout = {'x0': x0, 'y0': y0, 'cell': cell}
        M = n * (n * n + 1) // 2
        self.lbl_moves.configure(text=f"Moves : {self.move_count}")
        self.tk_images.clear() 

        for r in range(n):
            for c in range(n):
                x, y = x0 + c * cell, y0 + r * cell
                val = self.current_nums[r][c]
                char = self.num_to_char.get(val, "")

                if val in self.image_pieces:
                    resized_img = self.image_pieces[val].resize((int(cell), int(cell)), Image.LANCZOS)
                    tk_img = ImageTk.PhotoImage(resized_img)
                    self.tk_images.append(tk_img)
                    self.canvas.create_image(x, y, anchor="nw", image=tk_img)
                    text_color = "white"
                else:
                    bg = "#ffffff" if (r, c) != self.selected else "#FFF4E0"
                    self.canvas.create_rectangle(x, y, x+cell, y+cell, fill=bg, outline="", width=0)
                    text_color = "#333333"
                
                if (r, c) == self.selected:
                    self.canvas.create_rectangle(x, y, x+cell, y+cell, outline="#FF7676", width=3)
                
                self.canvas.create_text(x+cell/2, y+cell*0.2, text=str(val), 
                                        font=("Arial", int(cell*0.15), "bold"), fill=text_color)
                self.canvas.create_text(x+cell/2, y+cell*0.6, text=char, 
                                        font=("Times New Roman", int(cell*0.45), "bold"), fill=text_color)

        row_sums = [sum(row) for row in self.current_nums]
        col_sums = [sum(self.current_nums[r][c] for r in range(n)) for c in range(n)]
        for i in range(n):
            self.canvas.create_text(x0 + n*cell + 20, y0 + i*cell + cell/2, text=str(row_sums[i]), 
                                    fill=("#27AE60" if row_sums[i] == M else "#E74C3C"), font=("Arial", 14, "bold"))
            self.canvas.create_text(x0 + i*cell + cell/2, y0 - 20, text=str(col_sums[i]), 
                                    fill=("#27AE60" if col_sums[i] == M else "#E74C3C"), font=("Arial", 14, "bold"))
        
        self.check_win_status()

    def undo(self):
        if self.undo_stack:
            (r1, c1), (r2, c2) = self.undo_stack.pop()
            self.current_nums[r1][c1], self.current_nums[r2][c2] = self.current_nums[r2][c2], self.current_nums[r1][c1]
            self.move_count -= 1
            self.redraw()

    def give_hint(self):
        if self.hint_count >= 3:
            messagebox.showwarning("Hint Limit", "คุณใช้สิทธิ์ Hint ครบ 3 ครั้งแล้ว!")
            return
        wrong_positions = [(r, c) for r in range(self.n) for c in range(self.n) if self.current_nums[r][c] != self.target_goal[r][c]]
        if not wrong_positions:
            messagebox.showinfo("Hint", "ทุกตำแหน่งถูกต้องอยู่แล้ว!")
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
                    messagebox.showinfo("Hint", f"ช่วยสลับให้แล้ว! (เหลืออีก {3 - self.hint_count} ครั้ง)")
                    return

    def check_win_status(self):
        n, M = self.n, self.n * (self.n * self.n + 1) // 2
        is_magic = (all(sum(r) == M for r in self.current_nums) and 
                    all(sum(self.current_nums[r][c] for r in range(n)) == M for c in range(n)) and
                    sum(self.current_nums[i][i] for i in range(n)) == M and
                    sum(self.current_nums[i][n-1-i] for i in range(n)) == M)
        
        if is_magic and not getattr(self, 'game_won', False):
            self.game_won = True  
            self.win_status_label.configure(text="✨ Magic Square Complete! ✨")
            self.trigger_victory_effects()
            self.card.after(300, lambda: messagebox.showinfo("Success!", f"ยินดีด้วยคุณ {self.player_name}\nคุณแก้โจทย์ Magic Square สำเร็จแล้ว!"))
        elif not is_magic:
            self.win_status_label.configure(text="")

    def trigger_victory_effects(self):
        self.particles = []
        W = self.canvas.winfo_width()
        H = self.canvas.winfo_height()
        colors = ["#FF5733", "#33FF57", "#3357FF", "#F3FF33", "#FF33F3", "#00FFFF", "#FFD700"]
        centers = [(W*0.25, H*0.3), (W*0.5, H*0.2), (W*0.75, H*0.3)]
        
        for cx, cy in centers:
            for _ in range(40):
                p = {
                    'x': cx, 'y': cy,
                    'vx': random.uniform(-6, 6), 
                    'vy': random.uniform(-6, 2),   
                    'color': random.choice(colors),
                    'size': random.uniform(3, 8),
                    'life': random.randint(30, 60) 
                }
                p['id'] = self.canvas.create_oval(cx, cy, cx+p['size'], cy+p['size'], fill=p['color'], outline="")
                self.particles.append(p)
                
        self.animate_fireworks()

    def animate_fireworks(self):
        if not hasattr(self, 'particles') or not self.particles:
            return
            
        active_particles = []
        for p in self.particles:
            p['life'] -= 1
            if p['life'] > 0:
                p['x'] += p['vx']
                p['y'] += p['vy']
                p['vy'] += 0.2  
                self.canvas.coords(p['id'], p['x'], p['y'], p['x']+p['size'], p['y']+p['size'])
                active_particles.append(p)
            else:
                self.canvas.delete(p['id'])
                
        self.particles = active_particles
        if self.particles:
            self.canvas.after(30, self.animate_fireworks)

    def export_to_pdf(self):
        folder = "pdf"
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        finish_time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        mode_label = self.mode 
        filename = f"Result_{self.player_name}_{self.n}x{self.n}_{mode_label}_{timestamp}.pdf"
        filepath = os.path.join(folder, filename)
        
        font_name = "Helvetica-Bold"
        try:
            if mode_label in ["Emoji", "Symbols", "Thai", "Japanese"]:
                if os.path.exists("C:/Windows/Fonts/seguisym.ttf"):
                    pdfmetrics.registerFont(TTFont('UnicodeFont', 'C:/Windows/Fonts/seguisym.ttf'))
                    font_name = 'UnicodeFont'
                elif os.path.exists("C:/Windows/Fonts/tahoma.ttf"):
                    pdfmetrics.registerFont(TTFont('UnicodeFont', 'C:/Windows/Fonts/tahoma.ttf'))
                    font_name = 'UnicodeFont'
        except Exception as e:
            print(f"Font Registration Error: {e}")

        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4

        bg_path = "images/background.jpg"
        if os.path.exists(bg_path):
            c.drawImage(bg_path, 0, 0, width=width, height=height, preserveAspectRatio=False)

        c.setFillColorRGB(1, 1, 1)
        c.rect(50, 50, width - 100, height - 100, fill=1, stroke=0)

        c.setFillColorRGB(0, 0, 0)
        c.setFont("Times-Bold", 35)
        c.drawCentredString(width / 2, height - 140, "Congratulations!")
        c.setFont("Times-Roman", 18)
        c.drawCentredString(width / 2, height - 175, "You complete the Magic square !!")

        grid_size = 280 
        start_x = (width - grid_size) / 2
        start_y = height - 510 
        cell_size = grid_size / self.n
        M = self.n * (self.n * self.n + 1) // 2

        c.setFillColorRGB(0.15, 0.68, 0.38)
        c.setFont("Helvetica-Bold", 12) 
        for i in range(self.n):
            c.drawCentredString(start_x + (i + 0.5) * cell_size, start_y + grid_size + 15, str(M))
            c.drawString(start_x + grid_size + 20, start_y + (self.n - 1 - i + 0.5) * cell_size - 4, str(M))

        for r in range(self.n):
            for c_idx in range(self.n):
                x = start_x + c_idx * cell_size
                y = start_y + (self.n - 1 - r) * cell_size 
                val = self.current_nums[r][c_idx]
                char = self.num_to_char.get(val, "")

                if val in self.image_pieces:
                    img_reader = ImageReader(self.image_pieces[val])
                    c.drawImage(img_reader, x, y, width=cell_size, height=cell_size)

                c.setStrokeColorRGB(0.9, 0.5, 0.5) 
                c.rect(x, y, cell_size, cell_size, stroke=1, fill=0)

                c.setFillColorRGB(1, 1, 1)
                c.setFont("Helvetica-Bold", 10) 
                c.drawString(x + 7, y + cell_size - 16, str(val))

                c.setFont(font_name, 36) 
                c.drawCentredString(x + cell_size/2, y + (cell_size/2) - 15, char)

        info_y = 190
        c.setFillColorRGB(0, 0, 0)
        c.setFont(font_name, 16)
        
        c.drawCentredString(width / 2, info_y, f"Name: {self.player_name}")
        
        info_y_2 = info_y - 40
        c.setFont(font_name, 14)
        c.drawString(start_x + 10, info_y_2, f"Size : {self.n}x{self.n}") 
        c.drawCentredString(width / 2, info_y_2, f"Mode : {mode_label}") 
        c.drawRightString(start_x + grid_size - 10, info_y_2, f"Moves : {self.move_count}") 

        c.setFont("Times-Italic", 10)
        c.drawRightString(width - 80, 80, f"Completed on: {finish_time_str}")

        c.save()
        try:
            os.startfile(filepath) 
        except Exception as e:
            print(f"Error opening PDF: {e}")
        messagebox.showinfo("Export Success", f"บันทึกไฟล์เรียบร้อย!")

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
        self.on_finish() # เรียก Callback เปลี่ยนหน้าจอ