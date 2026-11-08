from PIL import Image, ImageDraw, ImageFont
import os
import re

# ================= 顏色設定 =================
BLUE_LINE = (21, 101, 192)    # 深藍色邊框 (#1565C0)
LIGHT_BLUE = (227, 242, 253)  # 淺藍色背景 (#E3F2FD)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY_TEXT = (100, 100, 100)

# ================= 字體設定 =================
FONT_CANDIDATES = [
    "NotoSansTC-Bold.ttf",
    "C:/Windows/Fonts/msjhbd.ttc",
    "C:/Windows/Fonts/msjh.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
]

FONT_PATH = None
for path in FONT_CANDIDATES:
    if os.path.exists(path):
        FONT_PATH = path
        break

if not FONT_PATH:
    print("⚠️ 警告：找不到中文字體，文字可能會變成方塊！")
    FONT_PATH = "arial.ttf"

try:
    FONT_TITLE = ImageFont.truetype(FONT_PATH, 40)
    FONT_LABEL = ImageFont.truetype(FONT_PATH, 36)
    FONT_TEXT = ImageFont.truetype(FONT_PATH, 22)
    FONT_FOOTER = ImageFont.truetype(FONT_PATH, 18)
except Exception as e:
    print(f"⚠️ 字體載入失敗 ({e})，使用預設字體。")
    FONT_TITLE = ImageFont.load_default()
    FONT_LABEL = ImageFont.load_default()
    FONT_TEXT = ImageFont.load_default()
    FONT_FOOTER = ImageFont.load_default()

# ================= 🌟 核心：直接解析 JS 檔案獲取規則 =================
def load_weather_rules_from_js(js_path="weather-utils.js"):
    """從 weather-utils.js 中提取正則表達式與圖標對應"""
    rules = []
    if not os.path.exists(js_path):
        print(f"⚠️ 找不到 {js_path}，將回退到預設雲朵圖標。")
        return rules
        
    with open(js_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # 利用正則匹配 JS 裡的 { regex: /.../, icon: "..." }
    pattern = re.compile(r"\{\s*regex:\s*/(.+?)/[a-z]*\s*,\s*icon:\s*[\"'](.+?)[\"']\s*\}")
    matches = pattern.findall(content)
    
    for regex_str, icon in matches:
        # 清理 JS 中的轉義字元（例如 \/），並編譯為 Python 正則
        regex_str = regex_str.replace(r"\/", "/")
        try:
            rules.append((re.compile(regex_str), icon))
        except Exception as e:
            print(f"⚠️ 無法解析正則：{regex_str}，錯誤：{e}")
            
    print(f"✅ 已成功從 {js_path} 載入 {len(rules)} 條天氣圖標規則。")
    return rules

# 初始化時載入規則
WEATHER_RULES = load_weather_rules_from_js()

def get_weather_icon(weather_text):
    if not weather_text:
        return "cloud.png"
    
    # 按照規則順序匹配
    for regex, icon in WEATHER_RULES:
        if regex.search(weather_text):
            return icon
            
    return "cloud.png"

# ================= 輔助函數：文字自動換行 =================
def draw_text_wrap(draw, text, font, max_width, x, y, fill):
    words = list(text)
    lines = []
    current_line = ""
    for char in words:
        test_line = current_line + char
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = char
    lines.append(current_line)
    
    current_y = y
    for line in lines:
        draw.text((x, current_y), line, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), line, font=font)
        current_y += (bbox[3] - bbox[1]) + 10
    return current_y

# ================= 輔助函數：垂直繪製文字 =================
def draw_vertical_text(draw, text, font, x, y, fill):
    current_y = y
    for char in text:
        bbox = draw.textbbox((0, 0), char, font=font)
        char_x = x - (bbox[2] - bbox[0]) / 2
        draw.text((char_x, current_y), char, font=font, fill=fill)
        current_y += (bbox[3] - bbox[1]) + 15 
    return current_y

# ================= 讀取 TXT 資料 =================
def read_files():
    today_text = "暫無資料"
    tomorrow_text = "暫無資料"
    issue_time = ""
    
    if os.path.exists("weather2d.txt"):
        with open("weather2d.txt", "r", encoding="utf-8") as f:
            raw = f.read().replace("\ufeff", "").strip()
            
            issued_match = re.search(r"[（(]\s*發佈\/更新時間[:：]\s*([^）)]+)\s*[）)]", raw)
            if issued_match:
                issue_time = issued_match.group(1).strip()
                
            today_match = re.search(r"今日天氣預報\s*\n([\s\S]*?)(?=\n\s*(?:明日天氣預報|[（(]))", raw)
            if today_match:
                today_text = today_match.group(1).strip().replace("\n", " ")
                
            tomorrow_match = re.search(r"明日天氣預報\s*\n([\s\S]*?)(?=\n\s*[（(])", raw)
            if tomorrow_match:
                tomorrow_text = tomorrow_match.group(1).strip().replace("\n", " ")
                
    return today_text, tomorrow_text, issue_time

# ================= 主繪圖邏輯 =================
def create_image():
    today_text, tomorrow_text, issue_time = read_files()

    img_width = 900
    margin_x = 40
    table_width = img_width - (margin_x * 2)
    
    col1_w = 100
    col2_w = 150
    col3_w = table_width - col1_w - col2_w
    
    col1_x = margin_x
    col2_x = col1_x + col1_w
    col3_x = col2_x + col2_w

    temp_img = Image.new("RGB", (10, 10))
    temp_draw = ImageDraw.Draw(temp_img)
    
    def calc_text_height(text):
        words = list(text)
        lines = []
        current_line = ""
        max_w = col3_w - 40
        for char in words:
            test_line = current_line + char
            bbox = temp_draw.textbbox((0, 0), test_line, font=FONT_TEXT)
            if bbox[2] - bbox[0] <= max_w:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = char
        lines.append(current_line)
        return len(lines) * (FONT_TEXT.getbbox("高")[3] + 10) + 50

    today_h = max(calc_text_height(today_text), 150)
    tomorrow_h = max(calc_text_height(tomorrow_text), 150)
    
    row1_y = 140
    row2_y = row1_y + today_h
    table_height = today_h + tomorrow_h
    img_height = row2_y + tomorrow_h + 80

    img = Image.new("RGB", (img_width, img_height), WHITE)
    draw = ImageDraw.Draw(img)

    # 1. 標題
    title_text = "今明兩日天氣預報"
    bbox = draw.textbbox((0, 0), title_text, font=FONT_TITLE)
    draw.text(((img_width - (bbox[2]-bbox[0]))/2, 50), title_text, font=FONT_TITLE, fill=BLACK)

    # 2. 表格外框與內線
    draw.rectangle([margin_x, row1_y, margin_x + table_width, row1_y + table_height], outline=BLUE_LINE, width=2)
    draw.line([(margin_x, row2_y), (margin_x + table_width, row2_y)], fill=BLUE_LINE, width=1)
    draw.line([(col2_x, row1_y), (col2_x, row1_y + table_height)], fill=BLUE_LINE, width=1)
    draw.line([(col3_x, row1_y), (col3_x, row1_y + table_height)], fill=BLUE_LINE, width=1)

    # 3. 今日資料
    draw.rectangle([margin_x+1, row1_y+1, col2_x-1, row2_y-1], fill=LIGHT_BLUE)
    draw_vertical_text(draw, "今日", FONT_LABEL, col1_x + col1_w/2, row1_y + (today_h - 100)/2, BLACK)
    
    icon_today = get_weather_icon(today_text)
    icon_path = os.path.join("weather icon", icon_today)
    if os.path.exists(icon_path):
        icon_img = Image.open(icon_path).convert("RGBA").resize((60, 60), Image.Resampling.LANCZOS)
        img.paste(icon_img, (int(col2_x + (col2_w - 60)/2), int(row1_y + (today_h - 60)/2)), icon_img)
        
    draw_text_wrap(draw, today_text, FONT_TEXT, col3_w - 40, col3_x + 20, row1_y + 25, BLACK)

    # 4. 明日資料
    draw.rectangle([margin_x+1, row2_y+1, col2_x-1, row2_y+tomorrow_h-1], fill=LIGHT_BLUE)
    draw_vertical_text(draw, "明日", FONT_LABEL, col1_x + col1_w/2, row2_y + (tomorrow_h - 100)/2, BLACK)
    
    icon_tomorrow = get_weather_icon(tomorrow_text)
    icon_path = os.path.join("weather icon", icon_tomorrow)
    if os.path.exists(icon_path):
        icon_img = Image.open(icon_path).convert("RGBA").resize((60, 60), Image.Resampling.LANCZOS)
        img.paste(icon_img, (int(col2_x + (col2_w - 60)/2), int(row2_y + (tomorrow_h - 60)/2)), icon_img)
        
    draw_text_wrap(draw, tomorrow_text, FONT_TEXT, col3_w - 40, col3_x + 20, row2_y + 25, BLACK)

    # 5. 底部時間
    footer_y = row2_y + tomorrow_h + 15
    time_text = f"發佈/更新時間：{issue_time}"
    bbox = draw.textbbox((0, 0), time_text, font=FONT_FOOTER)
    draw.text((img_width - margin_x - (bbox[2]-bbox[0]), footer_y), time_text, font=FONT_FOOTER, fill=GRAY_TEXT)

    output_filename = "weather2d_graphic.png"
    img.save(output_filename)
    print(f"✅ 繪圖完成，已儲存為 {output_filename}")

if __name__ == "__main__":
    create_image()