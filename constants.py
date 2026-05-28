# constants.py

ALPHABET = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
SYMBOLS = list("★☆◆◇▲▼■□●○◎☯⚔⚒⚙⚓⚖♪♬♠♣♥♦♔♕♖")
EMOJI_SET = ["🌟", "🚀", "🎈", "🍎", "🍊", "🍇", "🐶", "🐱", "👍", "🏀", "🎨", "🎬", "🎸", "🍕", "🍦", "🛸"]
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

# ==========================================
# 🎨 CENTRALIZED BUTTON STYLES CONFIGURATION
# ==========================================
# คุณสามารถเปลี่ยนสี รูปร่าง และฟอนต์ของปุ่มทั้งหมดในระบบได้จากตรงนี้
BTN_STYLES = {
    # --- ปุ่มทั่วไป/ปุ่มหลักของหน้าต่าง ---
    "primary": {
        "fg_color": "#BEAEE2", "hover_color": "#575766", "text_color": "black",
        "corner_radius": 0, "border_width": 1, "border_color": "black", "font": ("Garamond", 18)
    },
    # --- ปุ่มยกเลิก / ปุ่มย้อนกลับ ---
    "cancel": {
        "fg_color": "#F9F9F9", "hover_color": "#8C8C8C", "text_color": "black",
        "corner_radius": 0, "border_width": 1, "border_color": "black", "font": ("Garamond", 18)
    },
    # --- ปุ่มหน้าต่างตารางคะแนน ---
    "leaderboard": {
        "fg_color": "#CDF0EA", "hover_color": "#575766", "text_color": "black",
        "corner_radius": 0, "border_width": 1, "border_color": "black", "font": ("Garamond", 18)
    },
    # --- ปุ่มออกจากเกม / ปิดโปรแกรม ---
    "exit": {
        "fg_color": "#FF807E", "hover_color": "#575766", "text_color": "black",
        "corner_radius": 0, "border_width": 1, "border_color": "black", "font": ("Garamond", 18)
    },
    # --- ปุ่มเปลี่ยนภาษา 🌐 ---
    "language": {
        "fg_color": "#F7DBF0", "hover_color": "#6B6B83", "text_color": "black",
        "corner_radius": 20, "font": ("Garamond", 14)
    },
    
    # --- ปุ่มภายในหน้าบอร์ดเกม (GameManager) ---
    "game_cancel": {
        "fg_color": "#F9F9F9", "hover_color": "#8C8C8C", "text_color": "black",
        "corner_radius": 0, "border_width": 1, "border_color": "black", "font": ("Garamond", 16)
    },
    "game_shuffle": {
        "fg_color": "#FF807E", "hover_color": "#E56262", "text_color": "black",
        "corner_radius": 0, "border_width": 1, "border_color": "black", "font": ("Garamond", 16)
    },
    "game_hint": {
        "fg_color": "#CDF0EA", "hover_color": "#219653", "text_color": "black",
        "corner_radius": 0, "border_width": 1, "border_color": "black", "font": ("Garamond", 18)
    },
    "game_undo": {
        "fg_color": "#F9F9F9", "hover_color": "#76769E", "text_color": "black",
        "corner_radius": 0, "border_width": 1, "border_color": "black", "font": ("Garamond", 18)
    },
    "game_submit": {
        "fg_color": "#BEAEE2", "hover_color": "#73B0D8", "text_color": "black",
        "corner_radius": 0, "border_width": 1, "border_color": "black", "font": ("Garamond", 18)
    },
    "game_dev": {
        "fg_color": "#333333", "hover_color": "#555555", "text_color": "yellow",
        "corner_radius": 4, "font": ("Arial", 10)
    }
}

MODE_OPTIONS = {
    "English": ["English", "Japanese", "Thai", "Emoji", "Symbols"],
    "日本語": ["英語", "日本語", "タイ語", "絵文字", "記号"],
    "ไทย": ["อังกฤษ", "ญี่ปุ่น", "ไทย", "อีโมจิ", "สัญลักษณ์"]
}

MODE_TO_ENGLISH = {
    # English
    "English": "English", "Japanese": "Japanese", "Thai": "Thai", "Emoji": "Emoji", "Symbols": "Symbols",
    # 日本語
    "英語": "English", "日本語": "Japanese", "タイ語": "Thai", "絵文字": "Emoji", "記号": "Symbols",
    # ไทย
    "อังกฤษ": "English", "ญี่ปุ่น": "Japanese", "ไทย": "Thai", "อีโมจิ": "Emoji", "สัญลักษณ์": "Symbols"
}

PATTERN_TO_ENGLISH = {
    # ภาษาอังกฤษ
    "Random All": "Random All", "Horizontal": "Horizontal", "Vertical": "Vertical", "Diagonal": "Diagonal",
    # ภาษาไทย
    "สลับทั้งหมด": "Random All", "แนวนอน": "Horizontal", "แนวตั้ง": "Vertical", "แนวทแยง": "Diagonal",
    # ภาษาญี่ปุ่น
    "すべてシャッフル": "Random All", "水平方向": "Horizontal", "垂直方向": "Vertical", "対角線方向": "Diagonal"
}

LANG_DB = {
    "English": {
        "welcome": "Welcome to Magic Square !",
        "start_btn": "Start !",
        "leaderboard": "Leaderboard",
        "exit": "Exit",
        "info_title": "Please enter the information",
        "name_label": "Name : ",
        "size_label": "Size : ",
        "mode_label": "Mode : ",
        "select_title": "Please select the picture",
        "cancel": "Cancel",
        "shuffle": "Shuffle",
        "moves": "Moves :",
        "target": "Target :",
        "undo" : "Undo",
        "hint" : "Hint",
        "hint_title": "Hint Limit",
        "hint_msg": "You've used all 3 hints!",
        "hint_success": "Hint used! ({} left)",
        "hint_none": "Every position is already correct!",
        "win_title": "Success!",
        "win_msg": "Success!\nCongratulations {}!\nYou solved the Magic Square!",
        "submit_error_title": "Result",
        "submit_error_msg": "Magic Square not completed yet!",
        "pdf_success_title": "Export Success",
        "pdf_success_msg": "File saved successfully!",
        "submit_name_title_error" : "Input Error",
        "submit_name_error" : "Please input your name !",
        "submit_info" : "Submit",
        "submit" : "Submit",
        "magic_complete": "🎉 Magic Square Completed! 🎉",
        "style_label_image" : "Play with a background picture to help you solve the puzzle.",
        "style_label_classic" : "Traditional challenge using only numbers.",
        "style_label_ui" : "Style",
        "btn_standard": "Standard",
        "btn_creative" : "Creative",
        "goodbye_con" : "🎉 Congratulations! 🎉", 
        "goodbye_label" : "You complete the Magic square !!",
        "goodbye_button" : "Thank you !",
        "pattern_label": "Pattern : ",
        "pattern_options": ["Random All", "Horizontal", "Vertical", "Diagonal"],
        "all_patterns": "🌐 All Patterns",
        "cert_success_title": "Export Success",
        "cert_success_msg": "The certificate image has been successfully created:",
    },
    "日本語": {
        "welcome": "マジック・スクエアへようこそ！", 
        "start_btn": "スタート !",
        "leaderboard": "ランキング", 
        "exit": "終了",
        "info_title": "情報を入力してください",
        "name_label": "名前 : ",
        "size_label": "サイズ : ",
        "mode_label": "モード : ",
        "select_title": "画像を選択してください", 
        "cancel": "キャンセル", 
        "shuffle": "シャッフル",
        "moves": "手数 :",
        "target": "合計値 :",
        "undo" : "元に戻す", 
        "hint" : "ヒント",
        "hint_title": "ヒント制限",
        "hint_msg": "ヒントは3回までです！",
        "hint_success": "ヒントを使いました！（残り {} 回）",
        "hint_none": "すべての位置が正しいです！",
        "win_title": "クリア！", 
        "win_msg": "おめでとうございます、{}さん！\n魔方陣を完成させました！",
        "submit_error_title": "判定", 
        "submit_error_msg": "まだ魔方陣が完成していません！",
        "pdf_success_title": "保存完了",
        "pdf_success_msg": "ファイルを保存しました！",
        "submit_name_title_error" : "入力エラー",
        "submit_name_error" : "名前を入力してください！",
        "submit_info" : "決定",
        "submit" : "決定",
        "magic_complete": "🎉 魔法陣が完成しました！ 🎉",
        "style_label_image" : "背景のイラストをヒントにしてパズルを解こう",
        "style_label_classic" : "数字だけを使った、伝統的な頭脳チャレンジ",
        "style_label_ui" : "スタイル",
        "btn_standard": "スタンダード",
        "btn_creative": "クリエイティブ",
        "goodbye_con" : "🎉 おめでとうございます！ 🎉", 
        "goodbye_label" : "魔方陣を完成させました！!",
        "goodbye_button" : "遊んでくれてありがとう！",
        "pattern_label": "ヒント配置 : ",
        "pattern_options": ["すべてシャッフル", "水平方向", "垂直方向", "対角線方向"],
        "all_patterns": "🌐 すべての配置",
        "cert_success_title": "エクスポート成功",
        "cert_success_msg": "賞状の画像が正常に作成されました:",
    },
    "ไทย": {
        "welcome": "ยินดีต้อนรับสู่จัตุรัสกล !",
        "start_btn": "เริ่มเกม !",
        "leaderboard": "ตารางคะแนน",
        "exit": "ออก",
        "info_title": "กรุณากรอกข้อมูล",
        "name_label": "ชื่อ : ",
        "size_label": "ขนาด : ",
        "mode_label": "โหมด : ",
        "select_title": "กรุณาเลือกรูปภาพ",
        "cancel": "ยกเลิก",
        "shuffle": "สลับตำแหน่ง", 
        "moves": "จำนวนก้าว :",
        "target": "ผลรวม :",
        "undo" : "ย้อนกลับ",
        "hint" : "ใบ้",
        "hint_title": "จำกัดคำใบ้",
        "hint_msg": "คุณใช้สิทธิ์คำใบ้ครบ 3 ครั้งแล้ว!",
        "hint_success": "ใบ้ตำแหน่งให้แล้ว (เหลืออีก {} ครั้ง)",
        "hint_none": "ทุกตำแหน่งถูกต้องแล้ว !",
        "win_title": "สำเร็จ !",
        "win_msg": "ยินดีด้วยคุณ {}!\nคุณแก้โจทย์สำเร็จแล้ว!",
        "submit_error_title": "ผลการตรวจสอบ",
        "submit_error_msg": "จัตุรัสกลยังไม่สมบูรณ์ !",
        "pdf_success_title": "บันทึกสำเร็จ",
        "pdf_success_msg": "บันทึกไฟล์เรียบร้อยแล้ว !",
        "submit_name_title_error" : "ข้อผิดพลาด",
        "submit_name_error" : "กรุณากรอกชื่อของคุณ !",
        "submit_info" : "ตกลง",
        "submit" : "ตกลง",
        "magic_complete": "🎉 คุณทำตารางเวทมนตร์สำเร็จแล้ว! 🎉",
        "style_label_image" : "เล่นกับภาพพื้นหลังเพื่อช่วยคุณไขปริศนา",
        "style_label_classic" : "ความท้าทายแบบดั้งเดิมโดยใช้ตัวเลขเท่านั้น",
        "style_label_ui" : "สไตล์",
        "btn_standard": "มาตรฐาน", 
        "btn_creative": "สร้างสรรค์",
        "goodbye_con" : "🎉 ยินดีด้วยด้วยครับ ! 🎉", 
        "goodbye_label" : "คุณแก้โจทย์จัตุรัสกลสำเร็จแล้ว !!",
        "goodbye_button" : "ขอบคุณที่ร่วมสนุกครับ !",
        "pattern_label": "รูปแบบคำใบ้ : ",
        "pattern_options": ["สลับทั้งหมด", "แนวนอน", "แนวตั้ง", "แนวทแยง"],
        "all_patterns": "🌐 ทุกรูปแบบ",
        "cert_success_title": "ส่งออกสำเร็จ",
        "cert_success_msg": "จัดทำภาพใบเกียรติบัตรเรียบร้อยแล้ว:",
    }
}