import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image
from game_manager import GameManager

# ----------------- App Initialization -----------------
app = ctk.CTk()
app.title("Magic Square Master")
app.after(0, lambda: app.state('zoomed'))

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
ctk.CTkLabel(start_card, text="Welcome to Magic Square !", font=("Garamond", 28, "bold"), text_color="black").pack(pady=(60, 20))

square_img_data = Image.open("images/start.png")
square_img = ctk.CTkImage(square_img_data, size=(180, 160))
ctk.CTkLabel(start_card, text="", image=square_img).pack(pady=20)

ctk.CTkButton(start_card, text="Start !", command=show_info, fg_color="#6B6B83", hover_color="#575766", text_color="white",corner_radius=0, width=160, height=45, border_width=1, border_color="black", font=("Garamond", 18)).pack(pady=(20, 20))

# ----------------- UI: Info (Page 2) -----------------
info = ctk.CTkFrame(app, fg_color="#2b2b2b")
if bg_img:
    ctk.CTkLabel(info, text="", image=bg_img).place(x=0, y=0, relwidth=1, relheight=1)

info_card = ctk.CTkFrame(info, fg_color="white", corner_radius=0, border_width=0)
info_card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.75, relheight=0.75)
ctk.CTkLabel(info_card, text="Please enter the information", font=("Garamond", 26, "bold"), text_color="black").pack(pady=(50, 30))

form_frame = ctk.CTkFrame(info_card, fg_color="transparent")
form_frame.pack(pady=10) 

ctk.CTkLabel(form_frame, text="Name : ", font=("Garamond", 18), text_color="black").grid(row=0, column=0, sticky="e", pady=15, padx=(0, 10))
name_entry = ctk.CTkEntry(form_frame, width=220, height=35, fg_color="#eaeaea", text_color="black", border_color="black", border_width=1, corner_radius=0)
name_entry.grid(row=0, column=1, sticky="w")

ctk.CTkLabel(form_frame, text="Size : ", font=("Garamond", 18), text_color="black").grid(row=1, column=0, sticky="e", pady=15, padx=(0, 10))
radio_var = ctk.IntVar(value=3) 
size_container = ctk.CTkFrame(form_frame, fg_color="transparent")
size_container.grid(row=1, column=1, sticky="w")
ctk.CTkRadioButton(size_container, text="3 x 3", variable=radio_var, value=3, text_color="black", border_color="black", fg_color="#4F759B", border_width_checked=5).pack(side="left", padx=(0, 10))
ctk.CTkRadioButton(size_container, text="4 x 4", variable=radio_var, value=4, text_color="black", border_color="black", fg_color="#4F759B", border_width_checked=5).pack(side="left", padx=10)
ctk.CTkRadioButton(size_container, text="5 x 5", variable=radio_var, value=5, text_color="black", border_color="black", fg_color="#4F759B", border_width_checked=5).pack(side="left", padx=10)

ctk.CTkLabel(form_frame, text="Mode : ", font=("Garamond", 18), text_color="black").grid(row=2, column=0, sticky="e", pady=15, padx=(0, 10))
mode_menu = ctk.CTkOptionMenu(form_frame, values=["English", "Japanese", "Thai", "Emoji", "Symbols"], fg_color="#eaeaea", text_color="black", button_color="#eaeaea", button_hover_color="#eaeaea", corner_radius=0, dropdown_fg_color="#eaeaea", dropdown_text_color="black")
mode_menu.grid(row=2, column=1, sticky="w")
mode_menu.set("English")

button_container = ctk.CTkFrame(info_card, fg_color="transparent")
button_container.pack(pady=40)
ctk.CTkButton(button_container, text="Cancel", fg_color="#A9A9A9", text_color="white", hover_color="#8C8C8C", width=140, height=45, border_width=1, border_color="black", corner_radius=0, font=("Garamond", 18), command=show_start).pack(side="left", padx=15)
ctk.CTkButton(button_container, text="Submit", fg_color="#8181A1", text_color="white", hover_color="#6B6B83", width=140, height=45, border_width=1, border_color="black", corner_radius=0, font=("Garamond", 18), command=validate_and_submit).pack(side="left", padx=15)

# ----------------- UI: Select (Page 3) -----------------
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
    raw_img = Image.open(img_path)
    ctk_img = ctk.CTkImage(light_image=raw_img, size=(160, 160))
    select.image_refs.append(ctk_img)
    img_btn = ctk.CTkButton(image_grid, text="", image=ctk_img, width=160, height=160, fg_color="transparent", hover_color="#eeeeee",corner_radius=5, border_width=1, border_color="#cccccc", command=lambda p=img_path: start_magic_game(p))
    img_btn.grid(row=i // 3, column=i % 3, padx=15, pady=15)

ctk.CTkButton(select_card, text="Cancel", fg_color="#A9A9A9", text_color="white", hover_color="#8C8C8C", width=140, height=45, border_width=1, border_color="black", corner_radius=0, font=("Garamond", 18), command=show_info).pack(pady=(20, 20), padx=50, anchor="sw")

# ----------------- UI: Game Page (Page 4) -----------------
game = ctk.CTkFrame(app, fg_color="#2b2b2b")
if bg_img:
    ctk.CTkLabel(game, text="", image=bg_img).place(x=0, y=0, relwidth=1, relheight=1)

game_card = ctk.CTkFrame(game, fg_color="white", corner_radius=0, border_width=0)
game_card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.92)

# โหลด GameManager โดยโยน Callback เปลี่ยนหน้าจอไปด้วย
game_manager = GameManager(game_card, on_cancel_callback=show_select, on_finish_callback=show_goodbye)

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

# ----------------- App Start -----------------
if __name__ == "__main__":
    show_start()
    app.mainloop()