import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random, os
import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

app = ctk.CTk()
app.title("Magic Square Master")
app.after(0, lambda: app.state('zoomed'))

# ----------------- Constants & Character Sets -----------------
ALPHABET = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
SYMBOLS = list("★☆◎◇◆○●▲▼■□")
EMOJI_SET = ["🌟", "🚀", "🎈", "🍎", "🍊", "🍇", "🐶", "🐱", "⚽", "🏀"]
THAI_SET = list("กขคฆงจฉชซญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬอฮ")
JAPANESE_SET = list("あいうえおかきくけこさしすせそたちつてと")

def get_fillers(mode):
    if mode == "Thai": return THAI_SET
    elif mode == "Japanese": return JAPANESE_SET
    elif mode == "Emoji": return EMOJI_SET
    elif mode == "Symbols": return SYMBOLS
    return ALPHABET

POP = {
    "canvas_bg":  "#fffaf5",
    "grid":       "#ff6f61", 
    "select":     "#ffebcd",
    "ok":         "#2e7d32",
    "ng":         "#d32f2f",
    "subtext":    "#222222"
}

# ----------------- Magic Square Logic -----------------
def generate_magic_square(n: int):
    if n == 4:
        grid = [[r * 4 + c + 1 for c in range(4)] for r in range(4)]
        flip = {(0, 0), (0, 3), (3, 0), (3, 3), (1, 1), (1, 2), (2, 1), (2, 2)}
        for r in range(4):
            for c in range(4):
                if (r, c) in flip: grid[r][c] = 17 - grid[r][c]
        return grid
    else:
        grid = [[0] * n for _ in range(n)]
        num, r, c = 1, 0, n // 2
        while num <= n * n:
            grid[r][c] = num
            num += 1
            nr, nc = (r - 1) % n, (c + 1) % n
            if grid[nr][nc] != 0: r = (r + 1) % n
            else: r, c = nr, nc
        return grid

def rotate_grid(grid, k):
    res = [row[:] for row in grid]
    for _ in range(k % 4):
        res = [list(row) for row in zip(*res[::-1])]
    return res

def finish_and_goodbye():
    show_goodbye()

# ----------------- Page Switch Logic -----------------
def hide_all():
    start.pack_forget()
    info.pack_forget()
    select.pack_forget()
    game.pack_forget()
    goodbye.pack_forget()

def show_start():
    hide_all()
    start.pack(fill="both", expand=True)

def show_info():
    hide_all()
    info.pack(fill="both", expand=True)

def show_select():
    hide_all()
    select.pack(fill="both", expand=True)

def validate_and_submit():
    if not name_entry.get().strip():
        messagebox.showwarning("Input Error", "Please input your name !")
    else:
        show_select()

def show_game():
    hide_all()
    game.pack(fill="both", expand=True)

def start_magic_game(image_path=None):
    player_name = name_entry.get()
    size = radio_var.get()
    mode = mode_menu.get()
    game_manager.start_new_game(player_name, size, mode, image_path)
    show_game()

def show_goodbye():
    hide_all()
    goodbye.pack(fill="both", expand=True)

def restart_app():
    name_entry.delete(0, 'end')
    show_start()

bg_img = None
bg_data = Image.open("images/background.jpg") 
bg_img = ctk.CTkImage(bg_data, size=(app.winfo_screenwidth(), app.winfo_screenheight()))

def resize_bg(event):
    if event.widget == app and app.winfo_exists():
        w, h = event.width, event.height
        
        if hasattr(app, '_last_w') and app._last_w == w and app._last_h == h:
            return
            
        app._last_w, app._last_h = w, h
        
        if 'bg_img' in globals() and bg_img is not None:
            if w > 100 and h > 100:  
                try:
                    bg_img.configure(size=(w, h))
                except Exception:
                    pass

app.bind("<Configure>", resize_bg)
# ----------------- Start (Page 1) -----------------
start = ctk.CTkFrame(app, fg_color="#2b2b2b")

if bg_img:
    ctk.CTkLabel(start, text="", image=bg_img).place(x=0, y=0, relwidth=1, relheight=1)

start_card = ctk.CTkFrame(start, fg_color="white", corner_radius=0, border_width=0)
start_card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.75, relheight=0.75)

ctk.CTkLabel(start_card, text="Welcome to Magic Square !", font=("Garamond", 28, "bold"), text_color="black").pack(pady=(60, 20))

square_img_data = Image.open("images/start.png")
square_img = ctk.CTkImage(square_img_data, size=(180, 160))
ctk.CTkLabel(start_card, text="", image=square_img).pack(pady=20)

ctk.CTkButton(start_card, text="Start !", command=show_info, fg_color="#6B6B83", hover_color="#575766", text_color="white",corner_radius=0, width=160, height=45, border_width=1, border_color="black", font=("Garamond", 18)).pack(pady=(20, 20))

# ----------------- Info (Page 2) -----------------
info = ctk.CTkFrame(app, fg_color="#2b2b2b")

if bg_img:
    ctk.CTkLabel(info, text="", image=bg_img).place(x=0, y=0, relwidth=1, relheight=1)

info_card = ctk.CTkFrame(info, fg_color="white", corner_radius=0, border_width=0)
info_card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.75, relheight=0.75)

ctk.CTkLabel(info_card, text="Please enter the information", font=("Garamond", 26, "bold"), text_color="black").pack(pady=(50, 30))

form_frame = ctk.CTkFrame(info_card, fg_color="transparent")
form_frame.pack(pady=10) 

ctk.CTkLabel(form_frame, text="Name : ", font=("Garamond", 18), text_color="black").grid(row=0, column=0, sticky="e", pady=15, padx=(0, 10))
name_entry = ctk.CTkEntry(form_frame, width=220, height=35, fg_color="#cbcbcb", text_color="black", border_color="black", border_width=1, corner_radius=0)
name_entry.grid(row=0, column=1, sticky="w")

ctk.CTkLabel(form_frame, text="Size : ", font=("Garamond", 18), text_color="black").grid(row=1, column=0, sticky="e", pady=15, padx=(0, 10))
radio_var = ctk.IntVar(value=3) 
size_container = ctk.CTkFrame(form_frame, fg_color="transparent")
size_container.grid(row=1, column=1, sticky="w")
ctk.CTkRadioButton(size_container, text="3 x 3", variable=radio_var, value=3, text_color="black", border_color="black", fg_color="#4F759B", border_width_checked=5).pack(side="left", padx=(0, 10))
ctk.CTkRadioButton(size_container, text="4 x 4", variable=radio_var, value=4, text_color="black", border_color="black", fg_color="#4F759B", border_width_checked=5).pack(side="left", padx=10)
ctk.CTkRadioButton(size_container, text="5 x 5", variable=radio_var, value=5, text_color="black", border_color="black", fg_color="#4F759B", border_width_checked=5).pack(side="left", padx=10)

ctk.CTkLabel(form_frame, text="Mode : ", font=("Garamond", 18), text_color="black").grid(row=2, column=0, sticky="e", pady=15, padx=(0, 10))
mode_menu = ctk.CTkOptionMenu(form_frame, values=["English", "Japanese", "Thai", "Emoji", "Symbols"], fg_color="#cbcbcb", text_color="black", button_color="#cbcbcb", button_hover_color="#e0e0e0", corner_radius=0, dropdown_fg_color="white", dropdown_text_color="black")
mode_menu.grid(row=2, column=1, sticky="w")
mode_menu.set("English")

button_container = ctk.CTkFrame(info_card, fg_color="transparent")
button_container.pack(pady=40)
ctk.CTkButton(button_container, text="Cancel", fg_color="#A9A9A9", text_color="white", hover_color="#8C8C8C", width=140, height=45, border_width=1, border_color="black", corner_radius=0, font=("Garamond", 18), command=show_start).pack(side="left", padx=15)
ctk.CTkButton(button_container, text="Submit", fg_color="#8181A1", text_color="white", hover_color="#6B6B83", width=140, height=45, border_width=1, border_color="black", corner_radius=0, font=("Garamond", 18), command=validate_and_submit).pack(side="left", padx=15)

# ----------------- Select (Page 3) -----------------
select = ctk.CTkFrame(app, fg_color="#2b2b2b")

if bg_img:
    ctk.CTkLabel(select, text="", image=bg_img).place(x=0, y=0, relwidth=1, relheight=1)

select_card = ctk.CTkFrame(select, fg_color="white", corner_radius=0, border_width=0)
select_card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85, relheight=0.85)

ctk.CTkLabel(select_card, text="Please select the picture", font=("Garamond", 28, "bold"), text_color="black").pack(pady=(40, 20))

image_grid = ctk.CTkFrame(select_card, fg_color="transparent")
image_grid.pack(pady=10, padx=20)

image_paths = [f"images/{i}.png" for i in range(1, 7)] 
select.image_refs = [] 

for i, img_path in enumerate(image_paths):
    try:
        raw_img = Image.open(img_path)
        ctk_img = ctk.CTkImage(light_image=raw_img, size=(160, 160))
        select.image_refs.append(ctk_img)
        
        img_btn = ctk.CTkButton(image_grid, text="", image=ctk_img, 
                                width=160, height=160,
                                fg_color="transparent", hover_color="#eeeeee",
                                corner_radius=5, border_width=1, border_color="#cccccc",
                                command=lambda p=img_path: start_magic_game(p))
        
        img_btn.grid(row=i // 3, column=i % 3, padx=15, pady=15)
        
    except Exception as e:
        err_btn = ctk.CTkButton(image_grid, text="Image\nNot Found", 
                                width=160, height=160, corner_radius=5,
                                fg_color="#f0f0f0", text_color="gray")
        err_btn.grid(row=i // 3, column=i % 3, padx=15, pady=15)

ctk.CTkButton(select_card, text="Cancel", 
              fg_color="#A9A9A9", text_color="white", hover_color="#8C8C8C", 
              width=140, height=45, border_width=1, border_color="black", 
              corner_radius=0, font=("Garamond", 18), 
              command=show_info).pack(pady=(20, 20), padx=50, anchor="sw")

# ----------------- Game Page (Page 4) -----------------
game = ctk.CTkFrame(app, fg_color="#2b2b2b")

if bg_img:
    ctk.CTkLabel(game, text="", image=bg_img).place(x=0, y=0, relwidth=1, relheight=1)

game_card = ctk.CTkFrame(game, fg_color="white", corner_radius=0, border_width=0)
game_card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.92)

class GameManager:
    def __init__(self, master_card):
        self.card = master_card
        self.n = 3
        self.move_count = 0
        self.hint_count = 0  
        self.selected = None
        self.undo_stack = []
        self.image_pieces = {}
        self.tk_images = []
        
        self.top_bar = ctk.CTkFrame(self.card, fg_color="transparent")
        self.top_bar.pack(fill="x", pady=(20, 10), padx=30)
        
        self.btn_back = ctk.CTkButton(self.top_bar, text="Cancel", width=90, height=35, 
                                      font=("Garamond", 16), command=show_select, 
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
                    self.canvas.create_rectangle(
                        x, y, x+cell, y+cell, 
                        fill=bg, 
                        outline="", 
                        width=0
                    )
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
        
        mode_label = mode_menu.get()
        filename = f"Result_{self.player_name}_{self.n}x{self.n}_{mode_label}_{timestamp}.pdf"
        filepath = os.path.join(folder, filename)
        
        custom_font = "Helvetica-Bold" 
        try:
            if os.name == "nt" and os.path.exists("C:/Windows/Fonts/tahoma.ttf"):
                pdfmetrics.registerFont(TTFont('UnicodeFont', 'C:/Windows/Fonts/tahoma.ttf'))
                custom_font = 'UnicodeFont'
        except Exception as e:
            print(f"Font Error: {e}")

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

        grid_size = 350
        start_x = (width - grid_size) / 2
        start_y = height - 550
        cell_size = grid_size / self.n
        M = self.n * (self.n * self.n + 1) // 2

        c.setFillColorRGB(0.15, 0.68, 0.38)
        c.setFont("Helvetica-Bold", 14)
        for i in range(self.n):
            c.drawCentredString(start_x + (i + 0.5) * cell_size, start_y + grid_size + 15, str(M))
            c.drawString(start_x + grid_size + 20, start_y + (self.n - 1 - i + 0.5) * cell_size - 5, str(M))

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
                c.setFont("Helvetica-Bold", 12)
                c.drawString(x + 8, y + cell_size - 18, str(val))

                c.setFont(custom_font, 42)
                c.drawCentredString(x + cell_size/2, y + (cell_size/2) - 15, char)

        info_y = 220 
        c.setFillColorRGB(0, 0, 0)
        c.setFont(custom_font, 16)
        
        c.drawCentredString(width / 2, info_y, f"Name: {self.player_name}")
        
        info_y_2 = info_y - 40
        c.drawString(start_x, info_y_2, f"Size : {self.n}x{self.n}")
        c.drawCentredString(width / 2, info_y_2, f"Mode : {mode_label}")
        c.drawRightString(start_x + grid_size, info_y_2, f"Moves : {self.move_count}")

        c.setFont("Times-Italic", 10)
        c.drawRightString(width - 80, 80, f"Completed on: {finish_time_str}")

        c.save()
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
        finish_and_goodbye()

game_manager = GameManager(game_card)

# -------------------- Goodbye (Page 5) -----------------
goodbye = ctk.CTkFrame(app, fg_color="#FFC7C7")

if bg_img:
    ctk.CTkLabel(goodbye, text="", image=bg_img).place(x=0, y=0, relwidth=1, relheight=1)

goodbye_card = ctk.CTkFrame(goodbye, fg_color="white", corner_radius=0, border_width=0)
goodbye_card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.75, relheight=0.75)

ctk.CTkLabel(goodbye_card, text="🎉 Congratulations! 🎉", font=("Garamond", 35, "bold"), text_color="#2e7d32").pack(pady=(80, 20))
ctk.CTkLabel(goodbye_card, text="You complete the Magic square !!", font=("Garamond", 18), text_color="black").pack(pady=10)

victory_img_data = Image.open("images/won.png") 
victory_img = ctk.CTkImage(victory_img_data, size=(200, 180)) 
ctk.CTkLabel(goodbye_card, text="", image=victory_img).pack(pady=20)

ctk.CTkButton(goodbye_card, text="Thank you !", width=200, height=50, 
              fg_color="#6B6B83", hover_color="#575766", text_color="white", 
              corner_radius=0, border_width=1, border_color="black", font=("Garamond", 18),
              command=restart_app).pack(pady=(20, 40))

# ----------------- App Start -----------------
show_start()
app.mainloop()