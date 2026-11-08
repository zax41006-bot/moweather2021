from PIL import Image, ImageDraw, ImageFont
import os
import re

# ================= 顏色設定 =================
BLUE_LINE = (21, 101, 192)    # 深藍色邊框 (#1565C0)
LIGHT_BLUE = (227, 242, 253)  # 淺藍色背景 (#E3F2FD)
RED_TEXT = (192, 0, 0)        # 氣溫紅 (#C00000)
BLUE_TEXT = (0, 0, 255)       # 濕度藍 (#0000FF)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY_TEXT = (100, 100, 100)

# ================= 字體設定 =================
FONT_CANDIDATES = [
    "NotoSansTC-Bold.ttf",
    "C:/Windows/Fonts/msjhbd.ttc", # Windows 微軟正黑體 (粗)
    "C:/Windows/Fonts/msjh.ttc",   # Windows 微軟正黑體
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
    FONT_TITLE = ImageFont.truetype(FONT_PATH, 48)
    FONT_OUTLOOK = ImageFont.truetype(FONT_PATH, 20)
    FONT_DATE = ImageFont.truetype(FONT_PATH, 24)
    # 🌟 關鍵修改：把氣溫/濕度字體從 28 縮小到 20，防止文字重疊
    FONT_TEMP = ImageFont.truetype(FONT_PATH, 20) 
    FONT_FOOTER = ImageFont.truetype(FONT_PATH, 18)
except Exception as e:
    print(f"⚠️ 字體載入失敗 ({e})，使用預設字體。")
    FONT_TITLE = ImageFont.load_default()
    FONT_OUTLOOK = ImageFont.load_default()
    FONT_DATE = ImageFont.load_default()
    FONT_TEMP = ImageFont.load_default()
    FONT_FOOTER = ImageFont.load_default()

# ================= 🌟 核心：用純 Python 重現 JS 的圖標匹配規則 =================
def get_weather_icon(weather_text):
    if not weather_text:
        return "cloud.png"
    
    t = weather_text
    if re.search(r"雷暴", t):
        return "rain3_thunder.png"
    if re.search(r"(短暫時間天晴|部分時間天晴|間中天晴|短暫天晴).*(幾陣雨|驟雨)|(幾陣雨|驟雨).*(短暫時間天晴|部分時間天晴)", t):
        return "Sun_cloud_rain.png"
    if re.search(r"幾陣驟雨|間中有驟雨|有驟雨|有幾陣雨|間中有雨|有雨|有微雨|有幾陣微雨", t):
        return "rain2.png"
    if re.search(r"煙霞|烟霞", t):
        return "Haze.png"
    if re.search(r"薄霧|薄雾", t):
        return "fog1.png"
    if re.search(r"霧|雾", t):
        return "fog2.png"
    if re.search(r"短暫時間天晴|部分時間天晴|間中天晴|短暫天晴|天晴，部分時間多雲", t):
        return "Sun_cloud.png"
    if re.search(r"天晴", t):
        return "Sun.png"
    
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
        current_y += (bbox[3] - bbox[1]) + 8
    return current_y

# ================= 讀取 TXT 資料 =================
def read_files():
    outlook = "暫無天氣展望資訊"
    if os.path.exists("forecast.txt"):
        with open("forecast.txt", "r", encoding="utf-8") as f:
            text = f.read().replace("\ufeff", "").strip()
            parts = text.split("\n\n")
            if len(parts) >= 2:
                outlook = parts[1].replace("\n", " ").replace("\r", "")

    days = []
    issue_time = ""
    if os.path.exists("weather7d.txt"):
        with open("weather7d.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line: continue
                if "發佈/更新時間" in line:
                    issue_time = line.split("：")[-1].strip()
                elif "|" in line:
                    cols = [c.strip() for c in line.split("|")]
                    if len(cols) >= 6:
                        days.append({
                            "date": cols[0],
                            "weather": cols[1],
                            "temp_max": cols[2],
                            "temp_min": cols[3],
                            "humid_max": cols[4],
                            "humid_min": cols[5]
                        })
    return outlook, issue_time, days

# ================= 主繪圖邏輯 =================
def create_image():
    outlook, issue_time, days = read_files()
    
    if not days:
        days = [{"date":"-", "temp_min":"-", "temp_max":"-", "humid_min":"-", "humid_max":"-"}] * 7

    img_width = 1200
    margin_x = 30
    table_width = img_width - (margin_x * 2)
    col_width = table_width / 7
    
    row_h_outlook = 100
    row_h_date = 50
    row_h_icon = 80
    row_h_temp = 60
    row_h_humid = 60
    table_height = row_h_outlook + row_h_date + row_h_icon + row_h_temp + row_h_humid
    
    img_height = 140 + table_height + 80 
    
    img = Image.new("RGB", (img_width, img_height), WHITE)
    draw = ImageDraw.Draw(img)
    
    # 1. 繪製標題
    title_text = "七日天氣預報"
    bbox = draw.textbbox((0, 0), title_text, font=FONT_TITLE)
    draw.text(((img_width - (bbox[2]-bbox[0]))/2, 50), title_text, font=FONT_TITLE, fill=BLACK)
    
    # 2. 繪製表格
    start_y = 140
    start_x = margin_x
    
    draw.rectangle([start_x, start_y, start_x + table_width, start_y + table_height], outline=BLUE_LINE, width=2)
    
    y_curr = start_y
    draw.line([(start_x, y_curr + row_h_outlook), (start_x + table_width, y_curr + row_h_outlook)], fill=BLUE_LINE, width=1)
    y_curr += row_h_outlook
    draw.line([(start_x, y_curr + row_h_date), (start_x + table_width, y_curr + row_h_date)], fill=BLUE_LINE, width=1)
    y_curr += row_h_date
    draw.line([(start_x, y_curr + row_h_icon), (start_x + table_width, y_curr + row_h_icon)], fill=BLUE_LINE, width=1)
    y_curr += row_h_icon
    draw.line([(start_x, y_curr + row_h_temp), (start_x + table_width, y_curr + row_h_temp)], fill=BLUE_LINE, width=1)
    
    for i in range(1, 7):
        x_curr = start_x + (col_width * i)
        draw.line([(x_curr, start_y + row_h_outlook), (x_curr, start_y + table_height)], fill=BLUE_LINE, width=1)
        
    # 3. 填充資料
    draw.rectangle([start_x+1, start_y+1, start_x+table_width-1, start_y+row_h_outlook-1], fill=LIGHT_BLUE)
    draw_text_wrap(draw, outlook, FONT_OUTLOOK, table_width - 40, start_x + 20, start_y + 20, BLACK)
    
    y_date = start_y + row_h_outlook
    y_icon = y_date + row_h_date
    y_temp = y_icon + row_h_icon
    y_humid = y_temp + row_h_temp
    
    for i, day in enumerate(days[:7]):
        x_curr = start_x + (col_width * i)
        
        draw.rectangle([x_curr+1, y_date+1, x_curr+col_width-1, y_date+row_h_date-1], fill=LIGHT_BLUE)
        
        date_text = day.get("date", "")
        bbox = draw.textbbox((0, 0), date_text, font=FONT_DATE)
        draw.text((x_curr + (col_width - (bbox[2]-bbox[0]))/2, y_date + 10), date_text, font=FONT_DATE, fill=BLACK)
        
        # 🌟 使用純 Python 獲取圖標
        weather_desc = day.get("weather", "")
        icon_name = get_weather_icon(weather_desc)
        
        icon_path = os.path.join("weather icon", icon_name)
        if os.path.exists(icon_path):
            icon_img = Image.open(icon_path).convert("RGBA").resize((50, 50), Image.Resampling.LANCZOS)
            img.paste(icon_img, (int(x_curr + (col_width - 50)/2), int(y_icon + 15)), icon_img)
        else:
            # 如果找不到圖標，畫個圈並印出提示
            print(f"⚠️ 找不到圖標檔：{icon_path}")
            draw.ellipse([x_curr+40, y_icon+15, x_curr+70, y_icon+45], outline=(200,200,200))
        
        temp_text = f"{day.get('temp_min')}°C ~ {day.get('temp_max')}°C"
        bbox = draw.textbbox((0, 0), temp_text, font=FONT_TEMP)
        draw.text((x_curr + (col_width - (bbox[2]-bbox[0]))/2, y_temp + 15), temp_text, font=FONT_TEMP, fill=RED_TEXT)
        
        humid_text = f"{day.get('humid_min')}% ~ {day.get('humid_max')}%"
        bbox = draw.textbbox((0, 0), humid_text, font=FONT_TEMP)
        draw.text((x_curr + (col_width - (bbox[2]-bbox[0]))/2, y_humid + 15), humid_text, font=FONT_TEMP, fill=BLUE_TEXT)

    # 4. 繪製底部資訊
    footer_y = start_y + table_height + 20
    
    time_text = f"發佈/更新時間：{issue_time}"
    bbox = draw.textbbox((0, 0), time_text, font=FONT_FOOTER)
    draw.text((img_width - margin_x - (bbox[2]-bbox[0]), footer_y), time_text, font=FONT_FOOTER, fill=GRAY_TEXT)
    
    source_text = "澳門氣象中心 MMC 發佈"
    bbox = draw.textbbox((0, 0), source_text, font=FONT_FOOTER)
    draw.text((img_width - margin_x - (bbox[2]-bbox[0]), footer_y + 30), source_text, font=FONT_FOOTER, fill=BLUE_TEXT)

    output_filename = "weather7d_graphic.png"
    img.save(output_filename)
    print(f"✅ 繪圖完成，已儲存為 {output_filename}")

if __name__ == "__main__":
    create_image()