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