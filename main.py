# main.py

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image
from game_manager import GameManager
from constants import LANG_DB

# ----------------- App Initialization -----------------
app = ctk.CTk()
app.title("Magic Square Master")
app.after(0, lambda: app.state('zoomed'))
current_language = "English"

# ----------------- Page Switch Logic -----------------
def hide_all():
    start.pack_forget()
    info.pack_forget()
    select.pack_forget()
    game.pack_forget()
    goodbye.pack_forget()
    leaderboard.pack_forget()

def end():
    hide_all()
    goodbye.pack()
    app.after(2000, app.destroy())

def show_leaderboard():
    hide_all()
    leaderboard.pack(fill="both", expand=True)

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
    texts = LANG_DB[current_language]
    if not name_entry.get().strip():
        messagebox.showwarning(texts["submit_name_title_error"], texts["submit_name_error"])
    else:
        if style_var.get() == "Image":
            show_select()
        else:
            start_magic_game(None)

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

def toggle_language():
    global current_language
    langs = ["English", "日本語", "ไทย"]
    idx = (langs.index(current_language) + 1) % len(langs)
    current_language = langs[idx]
    
    lang_btn.configure(text=f"🌐 {current_language}")
    
    update_all_ui()

def update_all_ui():
    texts = LANG_DB[current_language]
    
    welcome_label.configure(text=texts["welcome"])
    start_btn.configure(text=texts["start_btn"])
    lb_btn.configure(text=texts["leaderboard"])
    exit_btn.configure(text=texts["exit"])
    
    info_title_label.configure(text=texts["info_title"])
    name_label_ui.configure(text=texts["name_label"])
    size_label_ui.configure(text=texts["size_label"])
    mode_label_ui.configure(text=texts["mode_label"])
    
    info_cancel_btn.configure(text=texts["cancel"])
    info_submit_btn.configure(text=texts["submit_info"])
    
    select_title_label.configure(text=texts["select_title"])
    select_cancel_btn.configure(text=texts["cancel"])
    
    lb_back_btn.configure(text=texts["cancel"])
    
    game_manager.update_ui_language()

# ----------------- Background Setup -----------------
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

# ----------------- UI: Start (Page 1) -----------------
start = ctk.CTkFrame(app, fg_color="#2b2b2b")
if bg_img:
    ctk.CTkLabel(start, text="", image=bg_img).place(x=0, y=0, relwidth=1, relheight=1)

start_card = ctk.CTkFrame(start, fg_color="white", corner_radius=0, border_width=0)
start_card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.75, relheight=0.75)

lang_btn = ctk.CTkButton(start_card, text=f"🌐 {current_language}", 
                          width=100, height=32, command=toggle_language,
                          fg_color="#8181A1", corner_radius=20)
lang_btn.place(relx=0.95, rely=0.05, anchor="ne")

welcome_label = ctk.CTkLabel(start_card, text="Welcome to Magic Square !", font=("Garamond", 28, "bold"), text_color="black")
welcome_label.pack(pady=(60, 20))

square_img_data = Image.open("images/start.png")
square_img = ctk.CTkImage(square_img_data, size=(180, 160))
ctk.CTkLabel(start_card, text="", image=square_img).pack(pady=20)

start_btn = ctk.CTkButton(start_card, text="Start !", command=show_info, fg_color="#6B6B83", hover_color="#575766", text_color="white",corner_radius=0, width=160, height=45, border_width=1, border_color="black", font=("Garamond", 18))
start_btn.pack(pady=(10, 10))

lb_btn = ctk.CTkButton(start_card, text="Leaderboard", command=show_leaderboard, fg_color="#82F6BE", hover_color="#575766", text_color="white",corner_radius=0, width=160, height=45, border_width=1, border_color="black", font=("Garamond", 18))
lb_btn.pack(pady=(10, 10))

exit_btn = ctk.CTkButton(start_card, text="Exit", command=end, fg_color="#FF807E", hover_color="#575766", text_color="white",corner_radius=0, width=160, height=45, border_width=1, border_color="black", font=("Garamond", 18))
exit_btn.pack(pady=(10, 10))

# ----------------- UI: Info (Page 2) -----------------
info = ctk.CTkFrame(app, fg_color="#2b2b2b")
texts = LANG_DB[current_language]
if bg_img:
    ctk.CTkLabel(info, text="", image=bg_img).place(x=0, y=0, relwidth=1, relheight=1)

info_card = ctk.CTkFrame(info, fg_color="white", corner_radius=0, border_width=0)
info_card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.75, relheight=0.75)
info_title_label = ctk.CTkLabel(info_card, text="Please enter the information", font=("Garamond", 26, "bold"), text_color="black")
info_title_label.pack(pady=(50, 30))

form_frame = ctk.CTkFrame(info_card, fg_color="transparent")
form_frame.pack(pady=10)

# --- Name ---
name_label_ui = ctk.CTkLabel(form_frame, text="Name : ", font=("Garamond", 18), text_color="black")
name_label_ui.grid(row=0, column=0, sticky="e", pady=15, padx=(0, 10))
name_entry = ctk.CTkEntry(form_frame, width=220, height=35, fg_color="#eaeaea", text_color="black", border_color="black", border_width=1, corner_radius=0)
name_entry.grid(row=0, column=1, sticky="w")

# --- Size ---
size_label_ui = ctk.CTkLabel(form_frame, text="Size : ", font=("Garamond", 18), text_color="black")
size_label_ui.grid(row=1, column=0, sticky="e", pady=15, padx=(0, 10))
radio_var = ctk.IntVar(value=3)
size_container = ctk.CTkFrame(form_frame, fg_color="transparent")
size_container.grid(row=1, column=1, sticky="w")
ctk.CTkRadioButton(size_container, text="3 x 3", variable=radio_var, value=3, text_color="black", border_color="black", fg_color="#4F759B", border_width_checked=5).pack(side="left", padx=(0, 10))
ctk.CTkRadioButton(size_container, text="4 x 4", variable=radio_var, value=4, text_color="black", border_color="black", fg_color="#4F759B", border_width_checked=5).pack(side="left", padx=10)
ctk.CTkRadioButton(size_container, text="5 x 5", variable=radio_var, value=5, text_color="black", border_color="black", fg_color="#4F759B", border_width_checked=5).pack(side="left", padx=10)

# --- Type (Content Mode) ---
mode_label_ui = ctk.CTkLabel(form_frame, text="Type : ", font=("Garamond", 18), text_color="black")
mode_label_ui.grid(row=2, column=0, sticky="e", pady=15, padx=(0, 10))
mode_menu = ctk.CTkOptionMenu(form_frame, values=["English", "Japanese", "Thai", "Emoji", "Symbols"], fg_color="#eaeaea", text_color="black", button_color="#eaeaea", button_hover_color="#eaeaea", corner_radius=0, dropdown_fg_color="#eaeaea", dropdown_text_color="black")
mode_menu.grid(row=2, column=1, sticky="w")
mode_menu.set("English")

classic_label_ui = ctk.CTkLabel(form_frame, text=f"{texts['classic']}", font=("Garamond", 18), text_color="black")
classic_label_ui.grid(row=3, column=0, sticky="e", pady=15, padx=(0, 10))

# ตั้งค่าเริ่มต้นให้เป็น Image
style_var = ctk.StringVar(value="Image")

def update_style_desc():
    texts = LANG_DB[current_language]
    if style_var.get() == "Classic":
            style_desc_label.configure(text=f"{texts['style_label_classic']}")
    else:
        style_desc_label.configure(text=f"{texts['style_label_image']}")

# สร้าง Switch โดยใช้คำว่า "Classic Mode" เป็นหลัก
style_switch = ctk.CTkSwitch(form_frame, 
                             text="", # ตัดคำว่า ON/OFF หรือ Mode ออกตามสั่ง
                             variable=style_var, 
                             onvalue="Classic", 
                             offvalue="Image",
                             command=update_style_desc,
                             progress_color="#4F759B", 
                             button_color="white",
                             width=50) # ปรับความกว้างให้พอดีกับตัวสวิตช์เปล่า
style_switch.grid(row=3, column=1, sticky="w", pady=15)

# ส่วนแสดงคำอธิบาย (Description) ด้านล่างยังคงไว้เพื่อให้ User ทราบว่าเปิด/ปิดแล้วเกิดอะไรขึ้น
style_desc_label = ctk.CTkLabel(info_card, text="Play with a background picture to help you solve the puzzle.", 
                                font=("Garamond", 14), text_color="gray", wraplength=400)
style_desc_label.pack(pady=(0, 10))

# --- Buttons ---
button_container = ctk.CTkFrame(info_card, fg_color="transparent")
button_container.pack(pady=30)
info_cancel_btn = ctk.CTkButton(button_container, text="Cancel", fg_color="#A9A9A9", text_color="white", hover_color="#8C8C8C", width=140, height=45, border_width=1, border_color="black", corner_radius=0, font=("Garamond", 18), command=show_start)
info_cancel_btn.pack(side="left", padx=15)

info_submit_btn = ctk.CTkButton(button_container, text="Submit", fg_color="#8181A1", text_color="white", hover_color="#6B6B83", width=140, height=45, border_width=1, border_color="black", corner_radius=0, font=("Garamond", 18), command=validate_and_submit)
info_submit_btn.pack(side="left", padx=15)

# ----------------- UI: Select (Page 3) -----------------
select = ctk.CTkFrame(app, fg_color="#2b2b2b")
if bg_img:
    ctk.CTkLabel(select, text="", image=bg_img).place(x=0, y=0, relwidth=1, relheight=1)

select_card = ctk.CTkFrame(select, fg_color="white", corner_radius=0, border_width=0)
select_card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85, relheight=0.85)
select_title_label = ctk.CTkLabel(select_card, text="Please select the picture", font=("Garamond", 28, "bold"), text_color="black")
select_title_label.pack(pady=(40, 20))

image_grid = ctk.CTkFrame(select_card, fg_color="transparent")
image_grid.pack(pady=10, padx=20)

image_paths = [f"images/{i}.png" for i in range(1, 7)] 
select.image_refs = [] 

for i, img_path in enumerate(image_paths):
    raw_img = Image.open(img_path)
    ctk_img = ctk.CTkImage(light_image=raw_img, size=(160, 160))
    select.image_refs.append(ctk_img)
    img_btn = ctk.CTkButton(image_grid, text="", image=ctk_img, width=160, height=160, fg_color="transparent", hover_color="#eeeeee",corner_radius=5, border_width=1, border_color="#cccccc", command=lambda p=img_path: start_magic_game(p))
    img_btn.grid(row=i // 3, column=i % 3, padx=15, pady=15)

select_cancel_btn = ctk.CTkButton(select_card, text="Cancel", fg_color="#A9A9A9", text_color="white", hover_color="#8C8C8C", width=140, height=45, border_width=1, border_color="black", corner_radius=0, font=("Garamond", 18), command=show_info)
select_cancel_btn.pack(pady=(20, 20), padx=50, anchor="sw")

# ----------------- UI: Game Page (Page 4) -----------------
game = ctk.CTkFrame(app, fg_color="#2b2b2b")
if bg_img:
    ctk.CTkLabel(game, text="", image=bg_img).place(x=0, y=0, relwidth=1, relheight=1)

game_card = ctk.CTkFrame(game, fg_color="white", corner_radius=0, border_width=0)
game_card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.92)

# โหลด GameManager โดยโยน Callback เปลี่ยนหน้าจอไปด้วย
game_manager = GameManager(game_card, show_info, show_goodbye, lambda: current_language)

# -------------------- UI: Goodbye (Page 5) -----------------
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

# -------------------- UI: Leaderboard (Integrated) -----------------
leaderboard = ctk.CTkFrame(app, fg_color="#2b2b2b")
if bg_img:
    ctk.CTkLabel(leaderboard, text="", image=bg_img).place(x=0, y=0, relwidth=1, relheight=1)

leaderboard_card = ctk.CTkFrame(leaderboard, fg_color="white", corner_radius=0, border_width=0)
leaderboard_card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85, relheight=0.8)

# --- แบ่งฝั่ง ซ้าย (Podium) และ ขวา (Table) ---
lb_left_panel = ctk.CTkFrame(leaderboard_card, fg_color="transparent")
lb_left_panel.pack(side="left", fill="both", expand=True, padx=20, pady=20)

lb_right_panel = ctk.CTkFrame(leaderboard_card, fg_color="transparent")
lb_right_panel.pack(side="right", fill="both", expand=True, padx=20, pady=20)

# --- ฝั่งซ้าย: แท่นรางวัล (Podium) ---
def create_podium_card(parent, rank, name, pts, color):
    card = ctk.CTkFrame(parent, fg_color=color, border_width=1, border_color="black", corner_radius=0)
    ctk.CTkLabel(card, text=rank, font=("Garamond", 40)).pack(pady=(10, 0))
    info = ctk.CTkFrame(card, fg_color="white", border_width=1, border_color="black", corner_radius=0)
    info.pack(fill="x", side="bottom", padx=5, pady=5)
    ctk.CTkLabel(info, text=name, font=("Garamond", 18, "bold"), text_color="black").pack()
    ctk.CTkLabel(info, text=f"{pts} points", font=("Garamond", 12), text_color="gray").pack(pady=(0, 5))
    return card

podium_top = ctk.CTkFrame(lb_left_panel, fg_color="transparent")
podium_top.pack(fill="x", pady=(20, 10))
create_podium_card(podium_top, "🏆", "Kampan", "99,542", "#FCE079").pack(anchor="center", ipadx=30, ipady=10)

podium_bottom = ctk.CTkFrame(lb_left_panel, fg_color="transparent")
podium_bottom.pack(fill="x", pady=10)
create_podium_card(podium_bottom, "🥈", "Peter", "97,426", "#BAC7D5").pack(side="left", expand=True, padx=10, ipadx=30, ipady=10)
create_podium_card(podium_bottom, "🥉", "Sandy", "95,231", "#EAB293").pack(side="right", expand=True, padx=10, ipadx=30, ipady=10)

# รูปเด็กถือถ้วย (ถ้ามีไฟล์ won.png ก็นำมาใช้ได้)
lb_won_img_data = Image.open("images/won.png")
lb_won_img = ctk.CTkImage(lb_won_img_data, size=(120, 110))
ctk.CTkLabel(lb_left_panel, text="", image=lb_won_img).pack(side="bottom", pady=10)

# --- ฝั่งขวา: ตารางและ Filter ---
lb_border_frame = ctk.CTkFrame(lb_right_panel, fg_color="transparent", border_width=1, border_color="black", corner_radius=0)
lb_border_frame.pack(fill="both", expand=True)

# 1. Filter ส่วนบน
lb_filter_frame = ctk.CTkFrame(lb_border_frame, fg_color="transparent")
lb_filter_frame.pack(fill="x", padx=15, pady=15)

lb_mode_seg = ctk.CTkSegmentedButton(lb_filter_frame, values=["Image", "Classic"], 
                                     font=("Garamond", 15), fg_color="#9CA3AF", selected_color="#6B7280", height=35)
lb_mode_seg.set("Image")
lb_mode_seg.pack(fill="x", pady=(0, 10))

lb_size_seg = ctk.CTkSegmentedButton(lb_filter_frame, values=["3 x 3", "4 x 4", "5 x 5"], 
                                     font=("Garamond", 15), fg_color="#9CA3AF", selected_color="#6B7280", height=35)
lb_size_seg.set("3 x 3")
lb_size_seg.pack(fill="x")

# 2. ตารางคะแนน
lb_table_container = ctk.CTkFrame(lb_border_frame, fg_color="transparent", border_width=1, border_color="black", corner_radius=0)
lb_table_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

# Header ของตาราง
lb_header = ctk.CTkFrame(lb_table_container, fg_color="transparent")
lb_header.pack(fill="x", padx=10, pady=5)
ctk.CTkLabel(lb_header, text="Rank", font=("Garamond", 16, "bold"), text_color="black", width=50).pack(side="left")
ctk.CTkLabel(lb_header, text="Name", font=("Garamond", 16, "bold"), text_color="black", width=150, anchor="w").pack(side="left", padx=10)
ctk.CTkLabel(lb_header, text="Points", font=("Garamond", 16, "bold"), text_color="black", width=100, anchor="e").pack(side="right")

# แถวข้อมูล (Dummy Data)
dummy_list = [("4", "test", "test"), ("5", "test", "test"), ("6", "test", "test"), ("7", "test", "test"), ("8", "test", "test")]
for r, n, p in dummy_list:
    row = ctk.CTkFrame(lb_table_container, fg_color="transparent")
    row.pack(fill="x", padx=10, pady=2)
    ctk.CTkLabel(row, text=r, font=("Garamond", 14), text_color="black", width=50).pack(side="left")
    ctk.CTkLabel(row, text=n, font=("Garamond", 14), text_color="black", width=150, anchor="w").pack(side="left", padx=10)
    ctk.CTkLabel(row, text=p, font=("Garamond", 14), text_color="black", width=100, anchor="e").pack(side="right")

# ปุ่มย้อนกลับ (Back Button)
lb_back_btn = ctk.CTkButton(leaderboard_card, text="Cancel", fg_color="#A9A9A9", text_color="white", width=100, 
                            height=35, corner_radius=0, font=("Garamond", 16), command=show_start)
lb_back_btn.place(relx=0.02, rely=0.98, anchor="sw")

# ----------------- App Start -----------------
if __name__ == "__main__":
    show_start()
    app.mainloop()