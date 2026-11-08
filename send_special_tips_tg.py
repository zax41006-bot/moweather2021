import requests
import os
import re

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

WEBSITE_URL = "https://zax41006-bot.github.io/moweather2021/"

def send_telegram_message(text):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("✅ 特別天氣提示發送成功")
    else:
        print(f"❌ 發送失敗: {response.text}")

def read_file(filename):
    if not os.path.exists(filename): return ""
    with open(filename, "r", encoding="utf-8") as f:
        return f.read().replace("\ufeff", "").strip()

def save_last_content(filename, content):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

def build_special_tips_msg():
    raw_text = read_file("special-tips.txt")
    if not raw_text or raw_text == "-": 
        return None

    # 支援多個提示（用 --- 分隔）
    blocks = re.split(r'\n\s*-{3,}\s*\n', raw_text)
    
    msg = ""
    for i, block in enumerate(blocks):
        lines = block.strip().split('\n')
        if not lines: continue
        
        content_lines = []
        issued_time = ""
        
        for line in lines:
            line = line.strip()
            if not line: continue
            
            # 提取時間
            if "發佈/更新時間" in line or "發佈時間" in line:
                issued_time = line
            # 忽略原有的標題，我們自己加
            elif line == "[特別天氣提示]" or line == "[特别天气提示]":
                continue
            else:
                content_lines.append(line)
        
        content = "\n".join(content_lines)
        
        # 組裝排版（就像你的截圖一樣）
        msg += f"📢 <b>【特別天氣提示】</b>\n\n"
        msg += f"{content}\n\n"
        if issued_time:
            msg += f"🕒 {issued_time}\n"
        
        # 如果是多個提示，加上分隔線
        if i < len(blocks) - 1:
            msg += "\n━━━━━━━━━━━━━━\n\n"

    msg += f"\n🌐 <b>詳細資訊請瀏覽 MMC 官網：</b>\n{WEBSITE_URL}"
    return msg

if __name__ == "__main__":
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ 錯誤：未設定 TG_BOT_TOKEN 或 TG_CHAT_ID")
        exit(1)

    current_text = read_file("special-tips.txt")
    last_state = read_file("_last_special_tips.txt")

    if current_text == last_state:
        print("⏭️ 特別天氣提示未更新，跳過發送。")
        exit(0)

    print("🔄 偵測到特別天氣提示更新！開始發送...")
    
    if not current_text or current_text == "-":
        print("ℹ️ 目前無特別天氣提示，跳過發送。")
    else:
        msg = build_special_tips_msg()
        if msg:
            send_telegram_message(msg)

    save_last_content("_last_special_tips.txt", current_text)
    print("✅ 特別天氣提示任務完成！")