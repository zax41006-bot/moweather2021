import requests
import os
import re
import json

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

WEBSITE_URL = "https://zax41006-bot.github.io/moweather2021/"

def send_telegram_message(text):
    """發送純文字訊息"""
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("✅ 文字訊息發送成功")
    else:
        print(f"❌ 文字發送失敗: {response.text}")

def send_telegram_media_group(images, caption=""):
    """發送多張圖片相冊，可選在第一張帶 caption"""
    url = f"{BASE_URL}/sendMediaGroup"
    
    for i in range(0, len(images), 10):
        batch = images[i:i+10]
        media = []
        files = {}
        
        for j, img_path in enumerate(batch):
            attach_name = f"photo_{i+j}"
            files[attach_name] = open(img_path, 'rb')

            media_item = {
                "type": "photo",
                "media": f"attach://{attach_name}",
            }
            if i == 0 and j == 0 and caption:
                media_item["caption"] = caption
                media_item["parse_mode"] = "HTML"

            media.append(media_item)

        payload = {
            "chat_id": CHAT_ID,
            "media": json.dumps(media)
        }

        try:
            res = requests.post(url, data=payload, files=files)
            if res.status_code == 200:
                print(f"✅ 相冊發送成功（{len(batch)} 張）")
            else:
                print(f"❌ 相冊發送失敗: {res.text}")
        except Exception as e:
            print(f"❌ 相冊發送異常: {e}")
        finally:
            for f in files.values():
                f.close()

def read_file(filename):
    if not os.path.exists(filename):
        return ""
    with open(filename, "r", encoding="utf-8") as f:
        return f.read().replace("\ufeff", "").strip()

def save_last_content(filename, content):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

def find_special_tip_images(index):
    """尋找對應編號的所有圖片 (只認 .png，避免無限請求)"""
    images = []
    
    # 1. 找無後綴圖 (例如 special_tip_1.png)
    path = f"special_tip_{index}.png"
    if os.path.exists(path):
        images.append(path)
            
    # 2. 找分字母圖 (例如 special_tip_1-A.png)
    for letter in ['A', 'B', 'C', 'D', 'E', 'F']:
        path = f"special_tip_{index}-{letter}.png"
        if os.path.exists(path):
            images.append(path)
                
    return images

def build_special_tips_msg_and_images():
    """解析 special-tips.txt，回傳（完整文字訊息, 圖片路徑列表）"""
    raw_text = read_file("special-tips.txt")
    if not raw_text or raw_text == "-":
        return None, []

    blocks = re.split(r'\n\s*-{3,}\s*\n', raw_text)
    msg = ""
    all_images = []

    for i, block in enumerate(blocks, start=1):
        lines = block.strip().split('\n')
        if not lines:
            continue

        content_lines = []
        issued_time = ""

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if "發佈/更新時間" in line or "發佈時間" in line:
                issued_time = line
            elif line == "[特別天氣提示]" or line == "[特别天气提示]":
                continue
            else:
                content_lines.append(line)

        content = "\n".join(content_lines)
        if not content:
            continue

        msg += f"📢 <b>【特別天氣提示】</b>\n\n"
        msg += f"{content}\n\n"
        if issued_time:
            msg += f"🕒 {issued_time}\n"

        if i < len(blocks):
            msg += "\n━━━━━━━━━━━━━━\n\n"

        # 收集這個區塊的所有圖片
        imgs = find_special_tip_images(i)
        if imgs:
            all_images.extend(imgs)

    msg += f"\n🌐 <b>詳細資訊請瀏覽 MMC 官網：</b>\n{WEBSITE_URL}"
    return msg, all_images

def process_and_send():
    msg, images = build_special_tips_msg_and_images()
    if not msg:
        print("ℹ️ 無有效提示內容。")
        return

    # 情況一：完全沒有圖片
    if not images:
        send_telegram_message(msg)
        return

    # 情況二：有圖片，且文字 ≤ 1024 字
    if len(msg) <= 1024:
        if len(images) == 1:
            url = f"{BASE_URL}/sendPhoto"
            with open(images[0], 'rb') as photo:
                payload = {"chat_id": CHAT_ID, "caption": msg, "parse_mode": "HTML"}
                res = requests.post(url, data=payload, files={"photo": photo})
                if res.status_code == 200:
                    print("✅ 單張圖文發送成功")
                else:
                    print(f"❌ 發送失敗: {res.text}")
        else:
            send_telegram_media_group(images, msg)

    # 情況三：文字 > 1024 字，圖片無法帶 caption
    else:
        send_telegram_message(msg)
        if len(images) == 1:
            url = f"{BASE_URL}/sendPhoto"
            with open(images[0], 'rb') as photo:
                payload = {"chat_id": CHAT_ID}
                requests.post(url, data=payload, files={"photo": photo})
        else:
            send_telegram_media_group(images, "")

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
        process_and_send()

    save_last_content("_last_special_tips.txt", current_text)
    print("✅ 特別天氣提示任務完成！")