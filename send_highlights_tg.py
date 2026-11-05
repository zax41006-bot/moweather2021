import requests
import os

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

def send_telegram_photo(photo_path, caption):
    """發送圖片並附帶文字說明 (Caption)"""
    url = f"{BASE_URL}/sendPhoto"
    try:
        with open(photo_path, 'rb') as photo:
            payload = {
                "chat_id": CHAT_ID, 
                "caption": caption, 
                "parse_mode": "HTML"
            }
            files = {"photo": photo}
            res = requests.post(url, data=payload, files=files)
            if res.status_code != 200:
                print(f"❌ 圖片發送失敗 {photo_path}: {res.text}")
    except Exception as e:
        print(f"❌ 讀取圖片失敗 {photo_path}: {e}")

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

    # 按雙換行分割區塊 (保留原本的段落結構)
    blocks = [b.strip() for b in text_hl.split('\n\n') if b.strip()]
    
    if len(blocks) < 2: return

    # 1. 提取時間與副標題
    issue_time = blocks[0]
    sub_title = blocks[1]
    content_blocks = blocks[2:]

    # 2. 發送標題與發佈時間 (第一則訊息)
    header_msg = f"📢 <b>【澳門氣象中心 MMC】重點天氣預報</b>\n"
    header_msg += f"🕒 發佈時間：{issue_time}\n\n"
    header_msg += f"<b>{sub_title}</b>"
    send_telegram_message(header_msg)

    # 3. 逐段發送圖文內容
    for i, text in enumerate(content_blocks):
        img_path = find_image(i + 1)
        
        # 準備說明文字，第一段加上官網連結
        caption = text
        if i == 0:
            caption += f"\n\n🌐 <b>詳細資訊請瀏覽 MMC 官網：</b>\n{WEBSITE_URL}"
            
        # Telegram 圖片的 caption 限制為 1024 字元，如果太長會報錯
        if len(caption) > 1024:
            caption = caption[:1020] + "..."
        
        if img_path:
            # 如果有找到圖片，發送圖文
            print(f"正在發送圖片：{img_path}")
            send_telegram_photo(img_path, caption)
        else:
            # 沒有圖片，退化成純文字發送
            print(f"未找到圖片 highlight_{i+1}，以純文字發送。")
            # 如果是第一段，但沒有圖片，也要補上官網連結
            if i == 0 and WEBSITE_URL not in caption:
                caption += f"\n\n🌐 <b>詳細資訊請瀏覽 MMC 官網：</b>\n{WEBSITE_URL}"
            send_telegram_message(caption)


if __name__ == "__main__":
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ 錯誤：未設定 TG_BOT_TOKEN 或 TG_CHAT_ID")
        exit(1)

    # 取得最新內容與上次發送的狀態
    current_text = read_file("highlights.txt")
    last_state = read_file("_last_highlights.txt")

    # 如果沒更新，跳過
    if current_text == last_state:
        print("⏭️ 重點天氣預報未更新，跳過發送。")
        exit(0)

    print("🔄 偵測到重點天氣預報更新！開始發送...")
    
    process_and_send_highlights()
    
    # 發送完成後，更新備忘錄
    save_last_content("_last_highlights.txt", current_text)
    print("✅ 重點天氣預報任務完成！")