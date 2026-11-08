import requests
import os
import re
import json

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

WEBSITE_URL = "https://zax41006-bot.github.io/moweather2021/"

def read_file(filename):
    if not os.path.exists(filename): return ""
    with open(filename, "r", encoding="utf-8") as f:
        return f.read().replace("\ufeff", "").strip()

def save_last_content(filename, content):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

# 🌟 讀取並匹配 warning-icons.json
def get_warning_rule(text, rules):
    if not rules: return None
    raw = text.strip()
    for rule in rules:
        is_match = all(re.search(kw, raw) for kw in rule.get("matchAll", []))
        if is_match:
            return rule
    return None

# 🌟 發送圖片+文字 (或純文字)
def send_warning(text, image_name):
    image_path = os.path.join("weather icon", image_name) if image_name else None
    
    if image_name and os.path.exists(image_path):
        # 如果有圖片，使用 sendPhoto
        url = f"{BASE_URL}/sendPhoto"
        with open(image_path, 'rb') as photo:
            payload = {
                "chat_id": CHAT_ID,
                "caption": text,
                "parse_mode": "HTML"
            }
            res = requests.post(url, data=payload, files={"photo": photo})
    else:
        # 如果沒圖片，使用 sendMessage
        url = f"{BASE_URL}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        res = requests.post(url, json=payload)
        
    if res.status_code == 200:
        print(f"✅ 警報發送成功 (圖片: {image_name or '無'})")
    else:
        print(f"❌ 發送失敗: {res.text}")

def build_and_send_warnings():
    raw_text = read_file("warnings.txt")
    if not raw_text or raw_text == "-": 
        print("ℹ️ 目前無天氣警報。")
        return

    # 讀取圖片規則
    rules = []
    if os.path.exists("warning-icons.json"):
        with open("warning-icons.json", "r", encoding="utf-8") as f:
            rules = json.load(f)

    # 用 --- 分割多個警報
    blocks = re.split(r'\n\s*-{3,}\s*\n', raw_text)
    
    for block in blocks:
        block = block.strip()
        if not block: continue
        
        lines = block.split('\n')
        title = lines[0].strip()
        
        tag = ""
        content_start_idx = 1
        if len(lines) > 1 and lines[1].strip().startswith('#'):
            tag = lines[1].strip().replace('#', '')
            content_start_idx = 2
            
        content = "\n".join(lines[content_start_idx:]).strip()
        
        # 組裝單個警報的 HTML 文字
        msg = f"🚨 <b>【澳門氣象中心 MMC】天氣警報</b>\n\n"
        msg += f"<b>{title}</b>\n"
        if tag:
            msg += f"<b>【{tag}】</b>\n"
        msg += f"{content}\n\n"
        msg += f"🌐 <b>詳細資訊：</b>\n{WEBSITE_URL}"

        # 匹配圖片
        rule = get_warning_rule(block, rules)
        image_name = rule.get("image") if rule else None
        
        # 發送
        send_warning(msg, image_name)

if __name__ == "__main__":
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ 錯誤：未設定 TG_BOT_TOKEN 或 TG_CHAT_ID")
        exit(1)

    current_text = read_file("warnings.txt")
    last_state = read_file("_last_warnings.txt")

    if current_text == last_state:
        print("⏭️ 天氣警報未更新，跳過發送。")
        exit(0)

    print("🔄 偵測到天氣警報更新！開始發送...")
    build_and_send_warnings()
    
    save_last_content("_last_warnings.txt", current_text)
    print("✅ 天氣警報任務完成！")