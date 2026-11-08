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
        print("✅ 警報訊息發送成功")
    else:
        print(f"❌ 警報發送失敗: {response.text}")

def read_file(filename):
    if not os.path.exists(filename): return ""
    with open(filename, "r", encoding="utf-8") as f:
        return f.read().replace("\ufeff", "").strip()

def save_last_content(filename, content):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

def build_warnings_msg():
    raw_text = read_file("warnings.txt")
    if not raw_text or raw_text == "-": 
        return None

    # 用 --- 分割多個警報
    blocks = re.split(r'\n\s*-{3,}\s*\n', raw_text)
    
    msg = "🚨 <b>【澳門氣象中心 MMC】天氣警報</b>\n\n"
    
    for block in blocks:
        lines = block.strip().split('\n')
        if not lines: continue
        
        # 第一行通常是標題 (例如：MMC天氣警報)
        title = lines[0].strip()
        
        # 第二行如果有 # 就當作 Tag
        tag = ""
        content_start_idx = 1
        if len(lines) > 1 and lines[1].strip().startswith('#'):
            tag = lines[1].strip().replace('#', '')
            content_start_idx = 2
            
        # 剩下的行是內容
        content = "\n".join(lines[content_start_idx:]).strip()
        
        # 組裝單個警報區塊
        msg += f"<b>{title}</b>\n"
        if tag:
            msg += f"<b>【{tag}】</b>\n"
        msg += f"{content}\n\n"
        msg += "━━━━━━━━━━━━━━\n\n"

    msg = msg.strip() # 移除結尾多餘的換行
    msg += f"\n🌐 <b>詳細資訊請瀏覽 MMC 官網：</b>\n{WEBSITE_URL}"
    return msg

if __name__ == "__main__":
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ 錯誤：未設定 TG_BOT_TOKEN 或 TG_CHAT_ID")
        exit(1)

    current_text = read_file("warnings.txt")
    last_state = read_file("_last_warnings.txt")

    # 狀態沒變就跳過
    if current_text == last_state:
        print("⏭️ 天氣警報未更新，跳過發送。")
        exit(0)

    print("🔄 偵測到天氣警報更新！開始發送...")
    
    if not current_text or current_text == "-":
        # 如果清空了警報，可以選擇發送一條「目前無警報」的提示，或者直接跳過
        print("ℹ️ 目前無天氣警報，跳過發送。")
    else:
        msg = build_warnings_msg()
        if msg:
            send_telegram_message(msg)

    # 儲存狀態
    save_last_content("_last_warnings.txt", current_text)
    print("✅ 天氣警報任務完成！")