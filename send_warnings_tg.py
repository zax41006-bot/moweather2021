import requests
import os
import re
from datetime import datetime

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

WEBSITE_URL = "https://zax41006-bot.github.io/moweather2021/"
HISTORY_FILE = "warnings_history.txt"

def read_file(filename):
    if not os.path.exists(filename): return ""
    with open(filename, "r", encoding="utf-8") as f:
        return f.read().replace("\ufeff", "").strip()

def save_last_content(filename, content):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

def get_warning_rule(text, rules):
    if not rules: return None
    raw = text.strip()
    for rule in rules:
        is_match = all(re.search(kw, raw) for kw in rule.get("matchAll", []))
        if is_match:
            return rule
    return None

def send_warning(text, image_name):
    image_path = os.path.join("weather icon", image_name) if image_name else None
    
    if image_name and os.path.exists(image_path):
        url = f"{BASE_URL}/sendPhoto"
        with open(image_path, 'rb') as photo:
            payload = {"chat_id": CHAT_ID, "caption": text, "parse_mode": "HTML"}
            res = requests.post(url, data=payload, files={"photo": photo})
    else:
        url = f"{BASE_URL}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
        res = requests.post(url, json=payload)
        
    if res.status_code == 200:
        print(f"✅ 警報發送成功 (圖片: {image_name or '無'})")
    else:
        print(f"❌ 發送失敗: {res.text}")

# 🌟 解析時間並計算時長
def parse_time(time_str):
    try:
        return datetime.strptime(time_str, "%Y年%m月%d日%H時%M分")
    except:
        return datetime.now()

def calc_duration(start_str, end_str):
    start = parse_time(start_str)
    end = parse_time(end_str)
    delta = end - start
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    parts = []
    if days > 0: parts.append(f"{days}天")
    if hours > 0: parts.append(f"{hours}小時")
    if minutes > 0: parts.append(f"{minutes}分")
    return "".join(parts) if parts else "少於1分"

# 🌟 更新 TXT 歷史紀錄
def update_history_txt(tag, content, status):
    lines = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

    # 抓取內容中的時間
    time_match = re.search(r'(\d{4}年\d{1,2}月\d{1,2}日\d{1,2}時\d{1,2}分)', content)
    event_time = time_match.group(1) if time_match else datetime.now().strftime("%Y年%m月%d日%H時%M分")

    updated = False

    if status == "issued":
        # 檢查是否已經有一筆「生效中」的同類型警報
        exists = any(line.startswith(f"{tag}|") and "生效中" in line for line in lines)
        if not exists:
            # 新增一行：警報類型|發出時間|取消時間|總共生效
            lines.append(f"{tag}|{event_time}||生效中")
            updated = True

    elif status == "cancelled":
        # 尋找對應的「生效中」行並更新
        for i, line in enumerate(lines):
            if line.startswith(f"{tag}|") and "生效中" in line:
                parts = line.split('|')
                issue_time = parts[1]
                duration = calc_duration(issue_time, event_time)
                lines[i] = f"{tag}|{issue_time}|{event_time}|{duration}"
                updated = True
                break
        
        # 如果找不到對應的（例如手動新增的取消），就直接補上一行
        if not updated:
            lines.append(f"{tag}||{event_time}|已取消")
            updated = True

    if updated:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print(f"📝 歷史紀錄已更新 ({status})")

def build_and_send_warnings():
    raw_text = read_file("warnings.txt")
    rules = []
    if os.path.exists("warning-icons.json"):
        with open("warning-icons.json", "r", encoding="utf-8") as f:
            rules = json.load(f)

    if not raw_text or raw_text == "-":
        print("ℹ️ 目前無天氣警報。")
        return

    blocks = re.split(r'\n\s*-{3,}\s*\n', raw_text)
    
    for block in blocks:
        block = block.strip()
        if not block: continue
        
        lines = block.split('\n')
        tag = ""
        content_lines = []
        
        for line in lines:
            line = line.strip()
            if not line: continue
            if "MMC天氣警報" in line: continue
            if line.startswith('#'):
                tag = line.replace('#', '').strip()
            else:
                content_lines.append(line)
                
        content = "\n".join(content_lines)
        
        status = "cancelled" if "取消" in content else "issued"
        
        # 更新 TXT 歷史紀錄
        update_history_txt(tag, content, status)

        # 取得圖片與顏色
        rule = get_warning_rule(block, rules)
        image_name = rule.get("image") if rule else None
        level = rule.get("level") if rule else "yellow"

        # 發送 TG
        msg = f"🚨 <b>【澳門氣象中心 MMC】天氣警報</b>\n\n"
        if tag:
            msg += f"<b>【{tag}】</b>\n"
        msg += f"{content}\n\n"
        msg += f"🌐 <b>詳細資訊請瀏覽 MMC 官網：</b>\n{WEBSITE_URL}"
        
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