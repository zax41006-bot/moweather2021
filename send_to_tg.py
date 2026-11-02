import requests
import os
import re

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# 🌟 這裡已經修正為你真實的網站網址
WEBSITE_URL = "https://zax41006-bot.github.io/moweather2021/"

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

# ================= 產生「今明兩日」訊息 =================
def build_forecast_2d_msg():
    current_text = read_file("weather2d.txt")
    if not current_text: return None

    time_match = re.search(r"發佈/更新時間[：:]\s*(.*?)\)", current_text)
    issued_time = time_match.group(1).strip() if time_match else "請見官網"

    formatted = current_text.replace("今日天氣預報", "<b>今日天氣預報</b>")
    formatted = formatted.replace("明日天氣預報", "<b>明日天氣預報</b>")
    formatted = re.sub(r"\((發佈/更新時間：.*?)\)", "", formatted).strip()

    msg = f"📢 <b>【澳門氣象中心 MMC】今明兩日天氣預報</b>\n"
    msg += f"🕒 發佈時間：{issued_time}\n\n"
    msg += f"{formatted}\n\n"
    msg += f"🌐 <b>詳細資訊請瀏覽 MMC 官網：</b>\n{WEBSITE_URL}"
    return msg

# ================= 產生「七日天氣」訊息 =================
def build_forecast_7d_msg():
    text_7d = read_file("weather7d.txt")
    text_forecast = read_file("forecast.txt")
    
    if not text_7d or not text_forecast: return None

    lines = text_7d.split("\n")
    issued_time = lines[0].strip() if lines else "請見官網"
    outlook = "\n".join(lines[1:]).strip()

    days_text = ""
    for line in text_forecast.split("\n"):
        line = line.strip()
        if not line or line.startswith("發佈"): continue
        if "|" in line:
            cols = [c.strip() for c in line.split("|")]
            if len(cols) >= 6:
                days_text += f"\n <b>{cols[0]}</b>\n"
                days_text += f"{cols[1]}\n" 
                days_text += f"🌡️ 氣溫：{cols[3]}°C ~ {cols[2]}°C\n"
                days_text += f"💧 濕度：{cols[5]}% ~ {cols[4]}%\n"
                days_text += "━━━━━━━━━━━━━━\n"

    msg = f"📢 <b>【澳門氣象中心 MMC】七日天氣預報</b>\n"
    msg += f"🕒 發佈時間：{issued_time}\n\n"
    msg += f"<b>🌡️ 天氣展望：</b>\n{outlook}\n"
    msg += "━━━━━━━━━━━━━━\n"
    msg += f"<b>📊 每日詳細預報：</b>{days_text}"
    msg += f"\n🌐 <b>詳細資訊請瀏覽 MMC 官網：</b>\n{WEBSITE_URL}"
    return msg

if __name__ == "__main__":
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ 錯誤：未設定 TG_BOT_TOKEN 或 TG_CHAT_ID")
        exit(1)

    # 1. 取得三個檔案的最新內容
    text_2d = read_file("weather2d.txt")
    text_7d = read_file("weather7d.txt")
    text_forecast = read_file("forecast.txt")

    # 2. 將三個檔案的內容合併成一個大字串，用來做「整體狀態比對」
    current_state = f"{text_2d}||{text_7d}||{text_forecast}"
    last_state = read_file("_last_all.txt")

    # 3. 如果狀態完全沒變（例如你手動點擊測試，但沒改檔案），就跳過
    if current_state == last_state:
        print("⏭️ 三個 txt 檔案皆未更新，跳過發送。")
        exit(0)

    print("🔄 偵測到其中一個 txt 更新！將同時發送兩則預報。")

    # 4. 觸發發送（只要有更新，兩則都發）
    msg_2d = build_forecast_2d_msg()
    if msg_2d: 
        send_telegram_message(msg_2d, "今明兩日")

    msg_7d = build_forecast_7d_msg()
    if msg_7d: 
        send_telegram_message(msg_7d, "七日天氣")

    # 5. 儲存這次的總狀態，防止重複洗版
    save_last_content("_last_all.txt", current_state)
    print("✅ 本次任務完成，已更新狀態紀錄。")