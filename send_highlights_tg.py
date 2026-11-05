import requests
import os
import json

# 從 GitHub Actions 的 Secrets 讀取變數
BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# 你的真實網站網址
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
    if response.status_code != 200:
        print(f"❌ 文字發送失敗: {response.text}")

def send_telegram_media_group(images, caption):
    """發送多張圖片（相冊），並將文字綁定在第一張圖"""
    url = f"{BASE_URL}/sendMediaGroup"
    media = []
    files = {}
    
    for i, img_path in enumerate(images):
        attach_name = f"photo_{i}"
        files[attach_name] = open(img_path, 'rb')
        
        media_item = {
            "type": "photo",
            "media": f"attach://{attach_name}",
        }
        # 只有第一張圖攜帶完整的說明文字
        if i == 0:
            media_item["caption"] = caption
            media_item["parse_mode"] = "HTML"
            
        media.append(media_item)
        
    payload = {
        "chat_id": CHAT_ID,
        "media": json.dumps(media)
    }
    
    try:
        res = requests.post(url, data=payload, files=files)
        if res.status_code != 200:
            print(f"❌ 相冊發送失敗: {res.text}")
    except Exception as e:
        print(f"❌ 相冊發送異常: {e}")
    finally:
        # 確保檔案關閉
        for f in files.values():
            f.close()

def read_file(filename):
    if not os.path.exists(filename): return ""
    with open(filename, "r", encoding="utf-8") as f:
        return f.read().replace("\ufeff", "").strip()

def save_last_content(filename, content):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

def find_image(index):
    """尋找對應編號的圖片 (支援 png 或 jpg)"""
    for ext in ['.png', '.jpg']:
        path = f"highlight_{index}{ext}"
        if os.path.exists(path):
            return path
    return None

def process_and_send_highlights():
    text_hl = read_file("highlights.txt")
    if not text_hl: return

    blocks = [b.strip() for b in text_hl.split('\n\n') if b.strip()]
    if len(blocks) < 2: return

    issue_time = blocks[0]
    sub_title = blocks[1]
    content_blocks = blocks[2:]

    # 1. 把所有文字合併成一個超長字串
    full_text = f"📢 <b>【澳門氣象中心 MMC】重點天氣預報</b>\n"
    full_text += f"🕒 發佈時間：{issue_time}\n\n"
    full_text += f"<b>{sub_title}</b>\n\n"
    
    body_text = "\n\n".join(content_blocks)
    full_text += body_text
    full_text += f"\n\n🌐 <b>詳細資訊請瀏覽 MMC 官網：</b>\n{WEBSITE_URL}"

    # 2. 收集所有存在的圖片
    images = []
    for i in range(len(content_blocks)):
        img = find_image(i + 1)
        if img: images.append(img)

    if not images:
        # 如果完全沒有圖片，直接發純文字
        send_telegram_message(full_text)
        return

    # 3. 根據字數判斷發送策略
    if len(full_text) <= 1024:
        # 字數在限制內，把圖片打包成相冊（最多10張），文字放在第一張
        if len(images) > 1:
            # 大於1張圖，用相冊發送
            send_telegram_media_group(images, full_text)
        else:
            # 只有1張圖，直接發送
            url = f"{BASE_URL}/sendPhoto"
            with open(images[0], 'rb') as photo:
                payload = {"chat_id": CHAT_ID, "caption": full_text, "parse_mode": "HTML"}
                requests.post(url, data=payload, files={"photo": photo})
    else:
        # 如果文字超過 1024 字，圖片無法攜帶這麼長的說明
        # 策略：先發一條完整的長文字，再把所有圖片打包成無說明的相冊發送
        send_telegram_message(full_text)
        if len(images) > 1:
            send_telegram_media_group(images, "")
        else:
            url = f"{BASE_URL}/sendPhoto"
            with open(images[0], 'rb') as photo:
                payload = {"chat_id": CHAT_ID}
                requests.post(url, data=payload, files={"photo": photo})

if __name__ == "__main__":
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ 錯誤：未設定 TG_BOT_TOKEN 或 TG_CHAT_ID")
        exit(1)

    current_text = read_file("highlights.txt")
    last_state = read_file("_last_highlights.txt")

    if current_text == last_state:
        print("⏭️ 重點天氣預報未更新，跳過發送。")
        exit(0)

    print("🔄 偵測到重點天氣預報更新！開始發送...")
    process_and_send_highlights()
    save_last_content("_last_highlights.txt", current_text)
    print("✅ 重點天氣預報任務完成！")