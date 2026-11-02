import requests
import os
import re

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
WEBSITE_URL = "https://zax41006-bot.github.io/MMC-weather/"

def send_telegram_message(text, label):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print(f"✅ {label} 訊息發送成功")
    else:
        print(f"❌ {label} 發送失敗: {response.text}")

def read_file(filename):
    if not os.path.exists(filename): return ""
    with open(filename, "r", encoding="utf-8") as f:
        return f.read().replace("\ufeff", "").strip()

def save_last_content(filename, content):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

# ================= 處理「今明兩日」 =================
def process_forecast_2d():
    current_text = read_file("weather2d.txt")
    if not current_text: return

    last_text = read_file("_last_2d.txt")
    if current_text == last_text:
        print("⏭️ 今明兩日預報未更新，跳過。")
        return

    print("🔄 偵測到 weather2d.txt 更新！")
    
    # 提取 txt 裡的時間 (格式：發佈/更新時間：2026年10月20日17時00分)
    time_match = re.search(r"發佈/更新時間[：:]\s*(.*?)\)", current_text)
    issued_time = time_match.group(1).strip() if time_match else "請見官網"

    # 清理並排版文字
    formatted = current_text.replace("今日天氣預報", "☀️ <b>今日天氣預報</b>")
    formatted = formatted.replace("明日天氣預報", "🌙 <b>明日天氣預報</b>")
    # 移除原本的括號時間，我們在開頭統一顯示
    formatted = re.sub(r"\((發佈/更新時間：.*?)\)", "", formatted).strip()

    msg = f"📢 <b>【澳門氣象中心 MMC】今明兩日天氣預報</b>\n"
    msg += f"🕒 發佈時間：{issued_time}\n\n"
    msg += f"{formatted}\n\n"
    msg += f"🌐 <b>詳細資訊請瀏覽 MMC 官網：</b>\n{WEBSITE_URL}"
    
    send_telegram_message(msg, "今明兩日")
    save_last_content("_last_2d.txt", current_text)

# ================= 處理「七日天氣」 =================
def process_forecast_7d():
    text_7d = read_file("weather7d.txt")
    text_forecast = read_file("forecast.txt")
    
    if not text_7d or not text_forecast: return

    # 將兩份文件合併作為比對依據
    current_combined = f"{text_7d}||{text_forecast}"
    last_combined = read_file("_last_7d.txt")

    if current_combined == last_combined:
        print("⏭️ 七日天氣（含 forecast.txt）未更新，跳過。")
        return

    print("🔄 偵測到 weather7d.txt 或 forecast.txt 更新！")

    # 1. 提取時間 (weather7d.txt 第一行)
    lines = text_7d.split("\n")
    issued_time = lines[0].strip() if lines else "請見官網"

    # 2. 提取天氣展望 (weather7d.txt 剩下的部分)
    outlook = "\n".join(lines[1:]).strip()

    # 3. 提取每日預報 (解析 forecast.txt)
    days_text = ""
    for line in text_forecast.split("\n"):
        line = line.strip()
        if not line or line.startswith("發佈"): continue
        if "|" in line:
            cols = [c.strip() for c in line.split("|")]
            if len(cols) >= 6:
                days_text += f"\n📅 <b>{cols[0]}</b>\n"
                days_text += f"🌤️ {cols[1]}\n"
                days_text += f"🌡️ 氣溫：{cols[3]}°C ~ {cols[2]}°C\n"
                days_text += f"💧 濕度：{cols[5]}% ~ {cols[4]}%\n"
                days_text += "━━━━━━━━━━━━━━\n"

    # 4. 組裝訊息
    msg = f"📢 <b>【澳門氣象中心 MMC】七日天氣預報</b>\n"
    msg += f"🕒 發佈時間：{issued_time}\n\n"
    msg += f"<b>🌡️ 天氣展望：</b>\n{outlook}\n"
    msg += "━━━━━━━━━━━━━━\n"
    msg += f"<b>📊 每日詳細預報：</b>{days_text}"
    msg += f"\n🌐 <b>詳細資訊請瀏覽 MMC 官網：</b>\n{WEBSITE_URL}"

    send_telegram_message(msg, "七日天氣")
    save_last_content("_last_7d.txt", current_combined)

if __name__ == "__main__":
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ 錯誤：未設定 TG_BOT_TOKEN 或 TG_CHAT_ID")
        exit(1)

    process_forecast_2d()
    process_forecast_7d()