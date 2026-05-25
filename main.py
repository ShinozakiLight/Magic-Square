# main.py

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image
from game_manager import GameManager
from constants import LANG_DB, MODE_OPTIONS, MODE_TO_ENGLISH, BTN_STYLES # [แก้ไข] นำเข้า BTN_STYLES

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
    if current_language == "ไทย":
        title = "ยืนยันการปิดโปรแกรม"
        message = "คุณแน่ใจหรือไม่ว่าต้องการปิดโปรแกรม?"
    elif current_language == "日本語":
        title = "終了の確認"
        message = "本当にプログラムを閉じますか？"
    else:
        title = "Confirm Exit"
        message = "Are you sure you want to exit?"

    if messagebox.askyesno(title, message):
        app.destroy()

def show_leaderboard():
    hide_all()
    update_leaderboard_view() 
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
        return
    
    # เช็คว่าถ้าเลือกโหมด Creative ให้ไปหน้าเลือกรูป (show_select)
    # ถ้าเป็น Standard ให้เริ่มเกมได้เลย (start_magic_game)
    if style_var.get() == "Creative": 
        show_select()
    else:
        start_magic_game(None)

def show_game():
    hide_all()
    game.pack(fill="both", expand=True)

def start_magic_game(image_path=None):
    player_name = name_entry.get().strip()
    size = radio_var.get()
    selected_mode_text = mode_menu.get()
    chosen_mode_eng = MODE_TO_ENGLISH.get(selected_mode_text, "English")
    
    visual_style = style_var.get() 
    arrange_mode = arrange_menu.get() # 
    
    game_manager.start_new_game(player_name, size, chosen_mode_eng, image_path, visual_style, arrange_mode)
    show_game()

def show_goodbye():
    hide_all()
    goodbye.pack(fill="both", expand=True)

def restart_app():
    name_entry.delete(0, 'end')
    show_start()

def update_style_desc():
    current_texts = LANG_DB[current_language]
    if style_var.get() == "Standard":
        style_desc_label.configure(text=current_texts['style_label_classic'])
    else:
        style_desc_label.configure(text=current_texts['style_label_image'])

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
    style_label_ui.configure(text=texts["style_label_ui"])
    btn_standard.configure(text=texts["btn_standard"])
    btn_creative.configure(text=texts["btn_creative"])

    arrange_label_ui.configure(text=texts.get("pattern_label", "Pattern : "))
    arrange_menu.configure(values=texts.get("pattern_options", ["Random All", "Horizontal", "Vertical", "Diagonal"]))
    arrange_menu.set(texts.get("pattern_options", ["Random All", "Horizontal", "Vertical", "Diagonal"])[0])

    update_style_desc()
    lb_back_btn.configure(text=texts["cancel"])
    
    goodbye_con.configure(text=texts["goodbye_con"])
    goodbye_label.configure(text=texts["goodbye_label"])
    goodbye_button.configure(text=texts["goodbye_button"])

    current_selected_local = mode_menu.get()
    current_selected_eng = MODE_TO_ENGLISH.get(current_selected_local, "English")
    new_values = MODE_OPTIONS[current_language]
    mode_menu.configure(values=new_values)
    old_index = MODE_OPTIONS["English"].index(current_selected_eng)
    mode_menu.set(new_values[old_index])
    
    game_manager.update_ui_language()

# ----------------- Background Setup -----------------
bg_img = None
try:
    bg_data = Image.open("images/background.jpg") 
    bg_img = ctk.CTkImage(bg_data, size=(app.winfo_screenwidth(), app.winfo_screenheight()))
except Exception:
    print("Warning: Background image not found.")

def resize_bg(event):
    if event.widget == app and app.winfo_exists():
        w, h = event.width, event.height
        if hasattr(app, '_last_w') and app._last_w == w and app._last_h == h:
            return
        app._last_w, app._last_h = w, h
        if 'bg_img' in globals() and bg_img is not None:
            if w > 100 and h > 100:  
                try: bg_img.configure(size=(w, h))
                except Exception: pass

app.bind("<Configure>", resize_bg)

# ----------------- UI: Start (Page 1) -----------------
start = ctk.CTkFrame(app, fg_color="#2b2b2b")
if bg_img:
    ctk.CTkLabel(start, text="", image=bg_img).place(x=0, y=0, relwidth=1, relheight=1)

start_card = ctk.CTkFrame(start, fg_color="white", corner_radius=0, border_width=0)
start_card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.75, relheight=0.75)

lang_btn = ctk.CTkButton(start_card, text=f"🌐 {current_language}", width=100, height=32, command=toggle_language, **BTN_STYLES["language"])
lang_btn.place(relx=0.95, rely=0.05, anchor="ne")

welcome_label = ctk.CTkLabel(start_card, text="Welcome to Magic Square !", font=("Garamond", 28, "bold"), text_color="black")
welcome_label.pack(pady=(60, 20))

try:
    square_img_data = Image.open("images/start.png")
    square_img = ctk.CTkImage(square_img_data, size=(180, 160))
    ctk.CTkLabel(start_card, text="", image=square_img).pack(pady=20)
except Exception: pass

# [แก้ไขใช้ BTN_STYLES]
start_btn = ctk.CTkButton(start_card, text="Start !", command=show_info, width=160, height=45, **BTN_STYLES["primary"])
start_btn.pack(pady=(10, 10))

lb_btn = ctk.CTkButton(start_card, text="Leaderboard", command=show_leaderboard, width=160, height=45, **BTN_STYLES["leaderboard"])
lb_btn.pack(pady=(10, 10))

exit_btn = ctk.CTkButton(start_card, text="Exit", command=end, width=160, height=45, **BTN_STYLES["exit"])
exit_btn.pack(pady=(10, 10))

# ----------------- UI: Info (Page 2) -----------------
info = ctk.CTkFrame(app, fg_color="#2b2b2b")
if bg_img:
    ctk.CTkLabel(info, text="", image=bg_img).place(x=0, y=0, relwidth=1, relheight=1)

info_card = ctk.CTkFrame(info, fg_color="white", corner_radius=0, border_width=0)
info_card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.75, relheight=0.75)
info_title_label = ctk.CTkLabel(info_card, text="Please enter the information", font=("Garamond", 26, "bold"), text_color="black")
info_title_label.pack(pady=(50, 30))

form_frame = ctk.CTkFrame(info_card, fg_color="transparent")
form_frame.pack(pady=10)

name_label_ui = ctk.CTkLabel(form_frame, text="Name : ", font=("Garamond", 18), text_color="black")
name_label_ui.grid(row=0, column=0, sticky="e", pady=15, padx=(0, 10))
name_entry = ctk.CTkEntry(form_frame, width=220, height=35, fg_color="#eaeaea", text_color="black", border_color="black", border_width=1, corner_radius=0)
name_entry.grid(row=0, column=1, sticky="w")

size_label_ui = ctk.CTkLabel(form_frame, text="Size : ", font=("Garamond", 18), text_color="black")
size_label_ui.grid(row=1, column=0, sticky="e", pady=15, padx=(0, 10))
radio_var = ctk.IntVar(value=3)
size_container = ctk.CTkFrame(form_frame, fg_color="transparent")
size_container.grid(row=1, column=1, sticky="w")
ctk.CTkRadioButton(size_container, text="3 x 3", variable=radio_var, value=3, text_color="black", border_color="black", fg_color="#4F759B", border_width_checked=5).pack(side="left", padx=(0, 10))
ctk.CTkRadioButton(size_container, text="4 x 4", variable=radio_var, value=4, text_color="black", border_color="black", fg_color="#4F759B", border_width_checked=5).pack(side="left", padx=10)
ctk.CTkRadioButton(size_container, text="5 x 5", variable=radio_var, value=5, text_color="black", border_color="black", fg_color="#4F759B", border_width_checked=5).pack(side="left", padx=10)

mode_label_ui = ctk.CTkLabel(form_frame, text="Mode : ", font=("Garamond", 18), text_color="black")
mode_label_ui.grid(row=2, column=0, sticky="e", pady=15, padx=(0, 10))
mode_menu = ctk.CTkOptionMenu(form_frame, values=["English", "Japanese", "Thai", "Emoji", "Symbols"], fg_color="#eaeaea", text_color="black", button_color="#eaeaea", button_hover_color="#eaeaea", corner_radius=0, dropdown_fg_color="#eaeaea", dropdown_text_color="black")
mode_menu.grid(row=2, column=1, sticky="w")
mode_menu.set("English")

arrange_label_ui = ctk.CTkLabel(form_frame, text="Pattern : ", font=("Garamond", 18), text_color="black")
arrange_label_ui.grid(row=3, column=0, sticky="e", pady=15, padx=(0, 10))

# มีให้เลือกสุ่มทั้งหมด, แนวนอน, แนวตั้ง, แนวเฉียง
arrange_menu = ctk.CTkOptionMenu(
    form_frame, 
    values=["Horizontal", "Vertical", "Diagonal", "Random All"],     
    fg_color="#eaeaea", text_color="black", button_color="#eaeaea", 
    button_hover_color="#eaeaea", corner_radius=0, 
    dropdown_fg_color="#eaeaea", dropdown_text_color="black"
)
arrange_menu.grid(row=3, column=1, sticky="w")
arrange_menu.set("Horizontal")

style_label_ui = ctk.CTkLabel(form_frame, text="Style : ", font=("Garamond", 18), text_color="black")
style_label_ui.grid(row=4, column=0, sticky="e", pady=15, padx=(0, 10))

style_var = ctk.StringVar(value="Standard")

# ----------------- ส่วน UI ปุ่ม Style ที่สวยงามขึ้น -----------------
style_btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
style_btn_frame.grid(row=4, column=1, sticky="w", pady=15)

def select_style(choice):
    style_var.set(choice)
    if choice == "Standard":
        btn_standard.configure(fg_color="#A9A3FA", text_color="white", hover_color="#3A5A78")
        btn_creative.configure(fg_color="#eaeaea", text_color="black", hover_color="#d4d4d4")
    else:
        btn_standard.configure(fg_color="#eaeaea", text_color="black", hover_color="#d4d4d4")
        btn_creative.configure(fg_color="#A9A3FA", text_color="white", hover_color="#3A5A78")
    
    update_style_desc() 

# ปุ่ม Standard
btn_standard = ctk.CTkButton(style_btn_frame, text="Standard", font=("Garamond", 15, "bold"),
                             width=110, height=36, corner_radius=5,
                             fg_color="#A9A3FA", text_color="white", hover_color="#3A5A78",
                             command=lambda: select_style("Standard"))
btn_standard.pack(side="left", padx=(0, 10))

# ปุ่ม Creative
btn_creative = ctk.CTkButton(style_btn_frame, text="Creative", font=("Garamond", 15, "bold"),
                             width=110, height=36, corner_radius=5,
                             fg_color="#eaeaea", text_color="black", hover_color="#d4d4d4",
                             command=lambda: select_style("Creative"))
btn_creative.pack(side="left")
# ----------------------------------------------------------------

style_desc_label = ctk.CTkLabel(info_card, text="", font=("Garamond", 14), text_color="gray", wraplength=400)
style_desc_label.pack(pady=(0, 10))

update_style_desc()

button_container = ctk.CTkFrame(info_card, fg_color="transparent")
button_container.pack(pady=30)

info_cancel_btn = ctk.CTkButton(button_container, text="Cancel", width=140, height=45, command=show_start, **BTN_STYLES["cancel"])
info_cancel_btn.pack(side="left", padx=15)

info_submit_btn = ctk.CTkButton(button_container, text="Submit", width=140, height=45, command=validate_and_submit, **BTN_STYLES["primary"])
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
    try:
        raw_img = Image.open(img_path)
        ctk_img = ctk.CTkImage(light_image=raw_img, size=(160, 160))
        select.image_refs.append(ctk_img)
        img_btn = ctk.CTkButton(image_grid, text="", image=ctk_img, width=160, height=160, fg_color="transparent", hover_color="#eeeeee",corner_radius=5, border_width=1, border_color="#cccccc", command=lambda p=img_path: start_magic_game(p))
        img_btn.grid(row=i // 3, column=i % 3, padx=15, pady=15)
    except Exception:
        print(f"Warning: Missing image file {img_path}")

# [แก้ไขใช้ BTN_STYLES]
select_cancel_btn = ctk.CTkButton(select_card, text="Cancel", width=140, height=45, command=show_info, **BTN_STYLES["cancel"])
select_cancel_btn.pack(pady=(20, 20), padx=50, anchor="sw")

# ----------------- UI: Game Page (Page 4) -----------------
game = ctk.CTkFrame(app, fg_color="#2b2b2b")
if bg_img:
    ctk.CTkLabel(game, text="", image=bg_img).place(x=0, y=0, relwidth=1, relheight=1)

game_card = ctk.CTkFrame(game, fg_color="white", corner_radius=0, border_width=0)
game_card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.92)

game_manager = GameManager(game_card, show_info, show_goodbye, lambda: current_language)

# -------------------- UI: Goodbye (Page 5) -----------------
goodbye = ctk.CTkFrame(app, fg_color="#FFC7C7")
if bg_img:
    ctk.CTkLabel(goodbye, text="", image=bg_img).place(x=0, y=0, relwidth=1, relheight=1)

goodbye_card = ctk.CTkFrame(goodbye, fg_color="white", corner_radius=0, border_width=0)
goodbye_card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.75, relheight=0.75)

# แยกการสร้างและ pack ออกจากกัน เพื่อไม่ให้ตัวแปรกลายเป็น None
goodbye_con = ctk.CTkLabel(goodbye_card, text="🎉 Congratulations! 🎉", font=("Garamond", 35, "bold"), text_color="#2e7d32")
goodbye_con.pack(pady=(80, 20))

goodbye_label = ctk.CTkLabel(goodbye_card, text="You complete the Magic square !!", font=("Garamond", 18), text_color="black")
goodbye_label.pack(pady=10)

try:
    victory_img_data = Image.open("images/won.png") 
    victory_img = ctk.CTkImage(victory_img_data, size=(200, 180)) 
    ctk.CTkLabel(goodbye_card, text="", image=victory_img).pack(pady=20)
except Exception: 
    pass

# [แก้ไขใช้ BTN_STYLES]
goodbye_button = ctk.CTkButton(goodbye_card, text="Thank you !", width=200, height=50, command=restart_app, **BTN_STYLES["primary"])
goodbye_button.pack(pady=(20, 40))

# -------------------- UI: Leaderboard -----------------
import json
import os

leaderboard = ctk.CTkFrame(app, fg_color="#2b2b2b")
if bg_img:
    ctk.CTkLabel(leaderboard, text="", image=bg_img).place(x=0, y=0, relwidth=1, relheight=1)

leaderboard_card = ctk.CTkFrame(leaderboard, fg_color="white", corner_radius=0, border_width=0)
leaderboard_card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85, relheight=0.8)

# ตัวแปรสถานะสำหรับการกรอง Filter (Default เริ่มต้นที่ Standard 3x3)
current_filter_style = "Standard"
current_filter_size = "3x3"

# ฟังก์ชันดึงและอัปเดตข้อมูลตารางแบบ Dynamic
def update_leaderboard_view():
    # ล้างข้อมูลแถวเก่าที่ตกค้างออกให้หมดก่อนวาดใหม่
    for widget in lb_scroll_frame.winfo_children():
        widget.destroy()
        
    json_file = "leaderboard.json"
    if not os.path.exists(json_file):
        # ถ้ายังไม่มีใครเล่นเลยให้ขึ้นข้อความแจ้งเตือน
        ctk.CTkLabel(lb_scroll_frame, text="No records found. Be the first to play!", font=("Garamond", 16), text_color="gray").pack(pady=40)
        return
        
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            all_records = json.load(f)
    except:
        all_records = []
        
    # คัดกรองข้อมูลสเปก (Filter Style และ Size) ให้ตรงกับปุ่มที่ผู้ใช้กดเลือก
    # หมายเหตุ: ในโค้ดตัวเกมถ้าเลือกแบบรูปภาพระบบจะเก็บค่าลงฐานข้อมูลว่า "Image"
    target_style = "Image" if current_filter_style == "Creative" else "Standard"
    
    filtered_list = [
        item for item in all_records 
        if item.get("style") == target_style and item.get("size") == current_filter_size
    ]
    
    # 🏅 เรียงลำดับคะแนนจากสูงสุดลงไปต่ำสุด (Descend Sorting)
    filtered_list.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    # ไอคอนความสวยงามให้กับ 3 อันดับแรก
    rank_icons = {1: "👑 1", 2: "🥈 2", 3: "🥉 3"}
    
    # วนลูปวาดตารางรายชื่อผู้เล่นขึ้นหน้าจอตามลำดับคะแนนจริง
    for idx, item in enumerate(filtered_list, 1):
        row = ctk.CTkFrame(lb_scroll_frame, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=4)
        
        # คอลัมน์ลำดับ
        rank_text = rank_icons.get(idx, f"  {idx}")
        rank_font = ("Garamond", 14, "bold") if idx <= 3 else ("Garamond", 14)
        ctk.CTkLabel(row, text=rank_text, font=rank_font, text_color="black", width=60, anchor="w").pack(side="left")
        
        # คอลัมน์ชื่อผู้เล่น + ทิศทาง Pattern ที่เลือกเล่น
        pattern_emoji = {"Horizontal": "➡️", "Vertical": "⬇/", "Diagonal": "↘️", "Random All": "🔀"}.get(item.get("pattern"), "🔀")
        player_display = f"{item.get('name')}  ({pattern_emoji})"
        ctk.CTkLabel(row, text=player_display, font=("Garamond", 14), text_color="black", width=250, anchor="w").pack(side="left", padx=10)
        
        # คอลัมน์สถิติเวลาและจำนวนก้าว (Sub-info)
        sec = item.get('time', 0)
        time_str = f"{sec//60:02d}:{sec%60:02d}"
        stat_text = f"⏱️ {time_str} | 🐾 {item.get('moves')} steps"
        ctk.CTkLabel(row, text=stat_text, font=("Garamond", 12), text_color="gray", width=200, anchor="w").pack(side="left", padx=5)

        # คอลัมน์คะแนนรวมสุทธิ (ขวาสุด)
        score_font = ("Garamond", 15, "bold") if idx <= 3 else ("Garamond", 14)
        score_color = "#e65100" if idx <= 3 else "black"
        ctk.CTkLabel(row, text=f"{item.get('score'):,}", font=score_font, text_color=score_color, width=120, anchor="e").pack(side="right")

# ฟังก์ชันเมื่อผู้เล่นกดสลับปุ่มตัวเลือกด้านบน
def select_style_filter(style):
    global current_filter_style
    current_filter_style = style
    btn_std.configure(fg_color="#ff6f61" if style == "Standard" else "#eaeaea", text_color="white" if style == "Standard" else "black")
    btn_cre.configure(fg_color="#ff6f61" if style == "Creative" else "#eaeaea", text_color="white" if style == "Creative" else "black")
    update_leaderboard_view()

def select_size_filter(size):
    global current_filter_size
    current_filter_size = size
    btn_3x3.configure(fg_color="#2e7d32" if size == "3x3" else "#eaeaea", text_color="white" if size == "3x3" else "black")
    btn_4x4.configure(fg_color="#2e7d32" if size == "4x4" else "#eaeaea", text_color="white" if size == "4x4" else "black")
    btn_5x5.configure(fg_color="#2e7d32" if size == "5x5" else "#eaeaea", text_color="white" if size == "5x5" else "black")
    update_leaderboard_view()

# --- ส่วนของการจัดแต่ง Layout Widgets ด้านบนบอร์ด ---
lb_title = ctk.CTkLabel(leaderboard_card, text="🏆 HALL OF FAME 🏆", font=("Garamond", 26, "bold"), text_color="#2b2b2b")
lb_title.pack(pady=(15, 5))

# 1. แผงกรองแบ่งคลาสโหมดความสวยงาม (Standard vs Creative)
filter_frame_1 = ctk.CTkFrame(leaderboard_card, fg_color="transparent")
filter_frame_1.pack(pady=5)

btn_std = ctk.CTkButton(filter_frame_1, text="Standard Mode", width=140, height=32, corner_radius=15, font=("Garamond", 14, "bold"), command=lambda: select_style_filter("Standard"))
btn_std.pack(side="left", padx=5)
btn_cre = ctk.CTkButton(filter_frame_1, text="Creative Mode", width=140, height=32, corner_radius=15, font=("Garamond", 14, "bold"), command=lambda: select_style_filter("Creative"))
btn_cre.pack(side="left", padx=5)

# 2. แผงกรองขนาดตารางเลขเวทมนตร์ (3x3 vs 4x4 vs 5x5)
filter_frame_2 = ctk.CTkFrame(leaderboard_card, fg_color="transparent")
filter_frame_2.pack(pady=5)

btn_3x3 = ctk.CTkButton(filter_frame_2, text="3 x 3 Grid", width=100, height=30, corner_radius=5, font=("Garamond", 13), command=lambda: select_size_filter("3x3"))
btn_3x3.pack(side="left", padx=5)
btn_4x4 = ctk.CTkButton(filter_frame_2, text="4 x 4 Grid", width=100, height=30, corner_radius=5, font=("Garamond", 13), command=lambda: select_size_filter("4x4"))
btn_4x4.pack(side="left", padx=5)
btn_5x5 = ctk.CTkButton(filter_frame_2, text="5 x 5 Grid", width=100, height=30, corner_radius=5, font=("Garamond", 13), command=lambda: select_size_filter("5x5"))
btn_5x5.pack(side="left", padx=5)

# 3. จัดสร้างหัวข้อตารางคอลัมน์ (Table Header)
lb_table_container = ctk.CTkFrame(leaderboard_card, fg_color="#f5f5f5", border_color="#ccc", border_width=1, corner_radius=4)
lb_table_container.pack(fill="both", expand=True, padx=25, pady=(10, 65))

lb_header = ctk.CTkFrame(lb_table_container, fg_color="#e0e0e0", height=35, corner_radius=0)
lb_header.pack(fill="x", padx=0, pady=0)
ctk.CTkLabel(lb_header, text="  Rank", font=("Garamond", 15, "bold"), text_color="black", width=60, anchor="w").pack(side="left", padx=10)
ctk.CTkLabel(lb_header, text="Player Name (Pattern)", font=("Garamond", 15, "bold"), text_color="black", width=250, anchor="w").pack(side="left", padx=10)
ctk.CTkLabel(lb_header, text="Game Stats", font=("Garamond", 15, "bold"), text_color="black", width=200, anchor="w").pack(side="left", padx=5)
ctk.CTkLabel(lb_header, text="Total Points  ", font=("Garamond", 15, "bold"), text_color="black", width=120, anchor="e").pack(side="right", padx=10)

# 4. กล่องแบบ Scrollable เลื่อนแถวรายชื่อคนเล่นขึ้นลงได้ไม่จำกัด
lb_scroll_frame = ctk.CTkScrollableFrame(lb_table_container, fg_color="transparent", corner_radius=0)
lb_scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

# ปุ่มยกเลิกกลับไปหน้าแรก
lb_back_btn = ctk.CTkButton(leaderboard_card, text="Cancel", width=100, height=35, command=show_start, **BTN_STYLES["cancel"])
lb_back_btn.place(relx=0.02, rely=0.98, anchor="sw")

# สั่งตั้งค่าเปิดไฟเขียวไฮไลต์ปุ่มเริ่มต้นทันทีก่อนโชว์บอร์ด
select_style_filter("Standard")
select_size_filter("3x3")

if __name__ == "__main__":
    show_start()
    app.mainloop()