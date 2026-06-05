# main.py

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image
from game_manager import GameManager
from constants import LANG_DB, MODE_OPTIONS, MODE_TO_ENGLISH, BTN_STYLES 

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
    name = name_entry.get().strip()
    
    if not name:
        messagebox.showwarning(texts["submit_name_title_error"], texts["submit_name_error"])
        return
    
    if len(name) > 15:
        if current_language == "ไทย":
            messagebox.showwarning("ข้อผิดพลาด", "ชื่อผู้ใช้ต้องยาวไม่เกิน 15 ตัวอักษร !")
        elif current_language == "日本語":
            messagebox.showwarning("エラー", "名前は15文字以内にする必要があります！")
        else:
            messagebox.showwarning("Error", "Name must be 15 characters or less!")
        return
    
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
    
    if image_path is not None:
        visual_style = "Creative"
    else:
        visual_style = style_var.get() 
    
    selected_pattern_text = arrange_menu.get()
    pattern_mapping = {
        "แนวนอน": "Horizontal", "แนวตั้ง": "Vertical", "แนวเฉียง": "Diagonal", "สุ่มทั้งหมด": "Random All",
        "水平": "Horizontal", "垂直": "Vertical", "対角線": "Diagonal", "すべてシャッフル": "Random All",
        "Horizontal": "Horizontal", "Vertical": "Vertical", "Diagonal": "Diagonal", "Random All": "Random All"
    }
    chosen_pattern_eng = pattern_mapping.get(selected_pattern_text, "Horizontal")
    
    game_manager.start_new_game(player_name, size, chosen_mode_eng, image_path, visual_style, chosen_pattern_eng)
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

    old_pattern_text = arrange_menu.get()
    reverse_pattern_mapping = {
        "Horizontal": 0, "แนวนอน": 0, "水平": 0,
        "Vertical": 1, "แนวตั้ง": 1, "垂直": 1,
        "Diagonal": 2, "แนวเฉียง": 2, "対角線": 2,
        "Random All": 3, "สุ่มทั้งหมด": 3, "すべてシャッフル": 3
    }
    old_index = reverse_pattern_mapping.get(old_pattern_text, 0)

    arrange_label_ui.configure(text=texts.get("pattern_label", "Pattern : "))
    current_options = texts.get("pattern_options", ["Horizontal", "Vertical", "Diagonal", "Random All"])
    arrange_menu.configure(values=current_options)
    arrange_menu.set(current_options[old_index])
    
    lb_title.configure(text=f"🏅 {texts['leaderboard'].upper()} 🏅")
    
    pattern_labels = texts.get("pattern_options", ["Horizontal", "Vertical", "Diagonal", "Random All"])
    all_text = texts.get("all_patterns", "🌐 All Patterns")
    
    pattern_buttons["All"].configure(text=all_text)
    pattern_buttons["Horizontal"].configure(text=f"➡️ {pattern_labels[0]}")
    pattern_buttons["Vertical"].configure(text=f"⬇️ {pattern_labels[1]}")
    pattern_buttons["Diagonal"].configure(text=f"↘️ {pattern_labels[2]}")
    pattern_buttons["Random All"].configure(text=f"🔀 {pattern_labels[3]}")

    update_style_desc()
    lb_back_btn.configure(text=texts["cancel"])
    
    goodbye_con.configure(text=texts["goodbye_con"])
    goodbye_label.configure(text=texts["goodbye_label"])
    goodbye_button.configure(text=texts["goodbye_button"])

    current_selected_local = mode_menu.get()
    current_selected_eng = MODE_TO_ENGLISH.get(current_selected_local, "English")
    new_values = MODE_OPTIONS[current_language]
    mode_menu.configure(values=new_values)
    old_mode_index = MODE_OPTIONS["English"].index(current_selected_eng)
    mode_menu.set(new_values[old_mode_index])
    
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

start_btn = ctk.CTkButton(start_card, text="Start !", command=show_info, width=160, height=45, **BTN_STYLES["primary"])
start_btn.pack(pady=(10, 10))

lb_btn = ctk.CTkButton(start_card, text="Leaderboard", command=show_leaderboard, width=160, height=45, **BTN_STYLES["leaderboard"])
lb_btn.pack(pady=(10, 10))

exit_btn = ctk.CTkButton(start_card, text="Exit", command=end, width=160, height=45, **BTN_STYLES["exit"])
exit_btn.pack(pady=(10, 10))


# ----------------- UI: Info (Page 2) -----------------
def limit_name_length(*args):
    value = name_var.get()
    if len(value) > 15:
        name_var.set(value[:15])

name_var = ctk.StringVar()
name_var.trace_add("write", limit_name_length)

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

name_entry = ctk.CTkEntry(form_frame, width=220, height=35, textvariable=name_var, fg_color="#eaeaea", text_color="black", border_color="black", border_width=1, corner_radius=0)
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

btn_standard = ctk.CTkButton(style_btn_frame, text="Standard", font=("Garamond", 15, "bold"),
                             width=110, height=36, corner_radius=5,
                             fg_color="#A9A3FA", text_color="white", hover_color="#3A5A78",
                             command=lambda: select_style("Standard"))
btn_standard.pack(side="left", padx=(0, 10))

btn_creative = ctk.CTkButton(style_btn_frame, text="Creative", font=("Garamond", 15, "bold"),
                             width=110, height=36, corner_radius=5,
                             fg_color="#eaeaea", text_color="black", hover_color="#d4d4d4",
                             command=lambda: select_style("Creative"))
btn_creative.pack(side="left")

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

goodbye_button = ctk.CTkButton(goodbye_card, text="Thank you !", width=200, height=50, command=restart_app, **BTN_STYLES["primary"])
goodbye_button.pack(pady=(20, 40))

# -------------------- UI: Leaderboard -----------------
import json
import os

FONT_FAMILY = "Segoe UI" 

RANK_CONFIG = {
    1: {"fg": "#FFFDF2", "border": "#FCD34D", "text": "#D97706", "rank_str": "🥇 1st"}, 
    2: {"fg": "#F8FAFC", "border": "#CBD5E1", "text": "#475569", "rank_str": "🥈 2nd"}, 
    3: {"fg": "#FFF7ED", "border": "#FDBA74", "text": "#C2410C", "rank_str": "🥉 3rd"}  
}

leaderboard = ctk.CTkFrame(app, fg_color="#2b2b2b")
if bg_img:
    ctk.CTkLabel(leaderboard, text="", image=bg_img).place(x=0, y=0, relwidth=1, relheight=1)

leaderboard_card = ctk.CTkFrame(leaderboard, fg_color="white", corner_radius=12, border_width=0)
leaderboard_card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85, relheight=0.82)

current_filter_style = "Standard"
current_filter_size = "3x3"
current_filter_pattern = "All"  

def update_leaderboard_view():
    for widget in lb_scroll_frame.winfo_children():
        widget.destroy()
        
    json_file = "leaderboard.json"
    if not os.path.exists(json_file):
        ctk.CTkLabel(lb_scroll_frame, text="No records found.", font=(FONT_FAMILY, 15, "italic"), text_color="gray").pack(pady=50)
        return
        
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            all_records = json.load(f)
    except:
        all_records = []
        
    filtered_list = []
    for item in all_records:
        item_style = item.get("style")
        
        style_match = False
        if current_filter_style == "Standard":
            if item_style == "Standard":
                style_match = True
        elif current_filter_style == "Creative":
            if item_style in ["Creative", "Image"]:
                style_match = True

        item_size = str(item.get("size", "")).replace(" ", "")
        filter_size = current_filter_size.replace(" ", "")

        if style_match and item_size == filter_size:
            p_pattern = item.get("pattern", "Random All")
            
            pattern_group_mapping = {
                "Horizontal": "Horizontal", "แนวนอน": "Horizontal", "水平": "Horizontal",
                "Vertical": "Vertical", "แนวตั้ง": "Vertical", "垂直": "Vertical",
                "Diagonal": "Diagonal", "แนวเฉียง": "Diagonal", "対角線": "Diagonal",
                "Random All": "Random All", "สุ่มทั้งหมด": "Random All", "สลับทั้งหมด": "Random All", "すべてシャッフル": "Random All"
            }
            
            normalized_pattern = pattern_group_mapping.get(p_pattern, p_pattern)
            
            if current_filter_pattern == "All" or normalized_pattern == current_filter_pattern:
                filtered_list.append(item)
    
    filtered_list.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    for idx, item in enumerate(filtered_list, 1):
        if idx in RANK_CONFIG:
            bg_color = RANK_CONFIG[idx]["fg"]
            border_color = RANK_CONFIG[idx]["border"]
            text_color = RANK_CONFIG[idx]["text"]
            rank_display = RANK_CONFIG[idx]["rank_str"]
            font_weight = "bold"
        else:
            bg_color = "#FFFFFF"
            border_color = "#E2E8F0"
            text_color = "#1E293B"
            rank_display = f"    {idx}"
            font_weight = "normal"
            
        row = ctk.CTkFrame(lb_scroll_frame, fg_color=bg_color, border_color=border_color, border_width=1.5, corner_radius=10, height=42)
        row.pack(fill="x", padx=8, pady=4)
        row.pack_propagate(False) 
        
        ctk.CTkLabel(row, text=rank_display, font=(FONT_FAMILY, 13, "bold"), text_color=text_color, width=60, anchor="w").pack(side="left", padx=(15, 5))
        
        p_name = item.get("name", "Guest")
        ctk.CTkLabel(row, text=p_name, font=(FONT_FAMILY, 13, font_weight), text_color="#1E293B", width=130, anchor="w").pack(side="left", padx=5)
        
        p_pattern = item.get("pattern", "Random All")
        ctk.CTkLabel(row, text=p_pattern, font=(FONT_FAMILY, 13), text_color="#1E293B", width=100, anchor="w").pack(side="left", padx=5)
        
        p_size = item.get("size", "3x3")
        ctk.CTkLabel(row, text=p_size, font=(FONT_FAMILY, 13), text_color="#1E293B", width=60, anchor="w").pack(side="left", padx=5)
        
        p_mode = item.get("mode", "English")
        ctk.CTkLabel(row, text=p_mode, font=(FONT_FAMILY, 13), text_color="#1E293B", width=80, anchor="w").pack(side="left", padx=5)
        
        sec = item.get('time', 0)
        time_str = f"{sec//60:02d}:{sec%60:02d}"
        stat_text = f"⏱️ {time_str}  •  🐾 {item.get('moves')}"
        ctk.CTkLabel(row, text=stat_text, font=(FONT_FAMILY, 12), text_color="#64748B", width=120, anchor="w").pack(side="left", padx=5)

        if idx <= 3:
            score_color = "#10B981"
            score_font = (FONT_FAMILY, 14, "bold")
        else:
            score_color = "#94A3B8"
            score_font = (FONT_FAMILY, 13, "normal")
            
        score_str = f"{item.get('score', 0):,} pts"
        ctk.CTkLabel(row, text=score_str, font=score_font, text_color=score_color, width=100, anchor="e").pack(side="right", padx=20)

def select_style_filter(style):
    global current_filter_style
    current_filter_style = style
    btn_std.configure(fg_color="#F87171" if style == "Standard" else "#F1F5F9", text_color="white" if style == "Standard" else "#475569")
    btn_cre.configure(fg_color="#F87171" if style == "Creative" else "#F1F5F9", text_color="white" if style == "Creative" else "#475569")
    update_leaderboard_view()

def select_size_filter(size):
    global current_filter_size
    current_filter_size = size
    btn_3x3.configure(fg_color="#16A34A" if size == "3x3" else "#F1F5F9", text_color="white" if size == "3x3" else "#475569")
    btn_4x4.configure(fg_color="#16A34A" if size == "4x4" else "#F1F5F9", text_color="white" if size == "4x4" else "#475569")
    btn_5x5.configure(fg_color="#16A34A" if size == "5x5" else "#F1F5F9", text_color="white" if size == "5x5" else "#475569")
    update_leaderboard_view()

def select_pattern_filter(pat):
    global current_filter_pattern
    current_filter_pattern = pat
    for k, btn in pattern_buttons.items():
        if k == pat:
            btn.configure(fg_color="#0EA5E9", text_color="white")
        else:
            btn.configure(fg_color="#F1F5F9", text_color="#475569")
    update_leaderboard_view()

lb_title = ctk.CTkLabel(leaderboard_card, text="🏅 HALL OF FAME 🏅", font=(FONT_FAMILY, 24, "bold"), text_color="#1E293B")
lb_title.pack(pady=(15, 8))

filter_frame_1 = ctk.CTkFrame(leaderboard_card, fg_color="transparent")
filter_frame_1.pack(pady=3)
btn_std = ctk.CTkButton(filter_frame_1, text="Standard", width=130, height=30, corner_radius=15, font=(FONT_FAMILY, 12, "bold"), command=lambda: select_style_filter("Standard"))
btn_std.pack(side="left", padx=4)
btn_cre = ctk.CTkButton(filter_frame_1, text="Creative", width=130, height=30, corner_radius=15, font=(FONT_FAMILY, 12, "bold"), command=lambda: select_style_filter("Creative"))
btn_cre.pack(side="left", padx=4)

filter_frame_2 = ctk.CTkFrame(leaderboard_card, fg_color="transparent")
filter_frame_2.pack(pady=3)
btn_3x3 = ctk.CTkButton(filter_frame_2, text="3 x 3", width=95, height=26, corner_radius=6, font=(FONT_FAMILY, 11, "bold"), command=lambda: select_size_filter("3x3"))
btn_3x3.pack(side="left", padx=4)
btn_4x4 = ctk.CTkButton(filter_frame_2, text="4 x 4", width=95, height=26, corner_radius=6, font=(FONT_FAMILY, 11, "bold"), command=lambda: select_size_filter("4x4"))
btn_4x4.pack(side="left", padx=4)
btn_5x5 = ctk.CTkButton(filter_frame_2, text="5 x 5", width=95, height=26, corner_radius=6, font=(FONT_FAMILY, 11, "bold"), command=lambda: select_size_filter("5x5"))
btn_5x5.pack(side="left", padx=4)

filter_frame_3 = ctk.CTkFrame(leaderboard_card, fg_color="transparent")
filter_frame_3.pack(pady=(3, 12))

pattern_buttons = {}
patterns_spec = [
    ("All", "🌐 All Patterns"),
    ("Horizontal", "➡️ Horizontal"),
    ("Vertical", "⬇️ Vertical"),
    ("Diagonal", "↘️ Diagonal"),
    ("Random All", "🔀 Random All")
]

for key, label in patterns_spec:
    btn = ctk.CTkButton(filter_frame_3, text=label, width=95, height=24, corner_radius=12, font=(FONT_FAMILY, 11, "bold"), command=lambda k=key: select_pattern_filter(k))
    btn.pack(side="left", padx=3)
    pattern_buttons[key] = btn

lb_table_container = ctk.CTkFrame(leaderboard_card, fg_color="#F8FAFC", border_color="#E2E8F0", border_width=1, corner_radius=12)
lb_table_container.pack(fill="both", expand=True, padx=25, pady=(0, 60))

lb_header = ctk.CTkFrame(lb_table_container, fg_color="transparent", height=35)
lb_header.pack(fill="x", padx=5, pady=(5, 0))
lb_header.pack_propagate(False)

ctk.CTkLabel(lb_header, text="Rank", font=(FONT_FAMILY, 13, "bold"), text_color="#64748B", width=60, anchor="w").pack(side="left", padx=(15, 5))
ctk.CTkLabel(lb_header, text="Player Name", font=(FONT_FAMILY, 13, "bold"), text_color="#64748B", width=130, anchor="w").pack(side="left", padx=5)
ctk.CTkLabel(lb_header, text="Pattern", font=(FONT_FAMILY, 13, "bold"), text_color="#64748B", width=100, anchor="w").pack(side="left", padx=5)
ctk.CTkLabel(lb_header, text="Size", font=(FONT_FAMILY, 13, "bold"), text_color="#64748B", width=60, anchor="w").pack(side="left", padx=5)
ctk.CTkLabel(lb_header, text="Mode", font=(FONT_FAMILY, 13, "bold"), text_color="#64748B", width=80, anchor="w").pack(side="left", padx=5)
ctk.CTkLabel(lb_header, text="Game Stats", font=(FONT_FAMILY, 13, "bold"), text_color="#64748B", width=120, anchor="w").pack(side="left", padx=5)
ctk.CTkLabel(lb_header, text="Total Points", font=(FONT_FAMILY, 13, "bold"), text_color="#64748B", width=100, anchor="e").pack(side="right", padx=20)

lb_scroll_frame = ctk.CTkScrollableFrame(lb_table_container, fg_color="transparent", corner_radius=0)
lb_scroll_frame.pack(fill="both", expand=True, padx=4, pady=4)

lb_back_btn = ctk.CTkButton(leaderboard_card, text="Cancel", width=100, height=32, command=show_start, **BTN_STYLES["cancel"])
lb_back_btn.place(relx=0.02, rely=0.97, anchor="sw")

select_style_filter("Standard")
select_size_filter("3x3")
select_pattern_filter("All")

if __name__ == "__main__":
    show_start()
    app.mainloop()