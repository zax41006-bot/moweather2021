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

def send_telegram_photo(photo_path, caption=""):
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

    issue_time = blocks[0]
    sub_title = blocks[1]
    content_blocks = blocks[2:]

    # 🌟 核心修改：把所有文字合併成一個超長字串
    full_text = f"📢 <b>【澳門氣象中心 MMC】重點天氣預報</b>\n"
    full_text += f"🕒 發佈時間：{issue_time}\n\n"
    full_text += f"<b>{sub_title}</b>\n\n"
    
    # 將所有段落用雙換行拼接，完美保留空行
    body_text = "\n\n".join(content_blocks)
    full_text += body_text
    full_text += f"\n\n🌐 <b>詳細資訊請瀏覽 MMC 官網：</b>\n{WEBSITE_URL}"

    # 收集所有圖片路徑
    images = []
    for i in range(len(content_blocks)):
        img = find_image(i + 1)
        if img: images.append(img)

    # 🌟 判斷文字長度是否在 Telegram 圖片的限制內 (1024字元)
    if len(full_text) <= 1024 and len(images) > 0:
        # 字數允許且有大圖：直接把整段文字塞進第一張圖的說明裡 (圖文一體，不分家)
        print("字數允許，發送圖文合併訊息...")
        send_telegram_photo(images[0], full_text)
        
        # 如果還有其他圖片，發在後面 (不帶文字)
        for img in images[1:]:
            send_telegram_photo(img, "")
    else:
        # 字數超過 1024 或完全沒有圖片：先發一條完整的大文字，再發所有圖片
        print("字數過長或無圖片，先發送完整長文再發送圖片...")
        send_telegram_message(full_text)
        for img in images:
            send_telegram_photo(img, "")


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