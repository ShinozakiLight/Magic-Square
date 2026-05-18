# constants.py

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
        "submit_game" : "Submit",
        "magic_complete": "🎉 Magic Square Completed! 🎉",
        "style_label_image" : "Play with a background picture to help you solve the puzzle.",
        "style_label_classic" : "Traditional challenge using only numbers.",
        "classic" : "Classic"
    },
    "日本語": {
        "welcome": "魔方陣へようこそ！", 
        "start_btn": "スタート",
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
        "submit_game" : "決定",
        "magic_complete": "🎉 魔法陣が完成しました！ 🎉",
        "style_label_image" : "Play with a background picture to help you solve the puzzle.",
        "style_label_classic" : "Traditional challenge using only numbers.",
        "classic" : "Classic"
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
        "submit_game" : "ตกลง",
        "magic_complete": "🎉 คุณทำตารางเวทมนตร์สำเร็จแล้ว! 🎉",
        "style_label_image" : "Play with aก background picture to help you solve the puzzle.",
        "style_label_classic" : "Traditกional challenge using only numbers.",
        "classic" : "Clasกsic"
    }
}