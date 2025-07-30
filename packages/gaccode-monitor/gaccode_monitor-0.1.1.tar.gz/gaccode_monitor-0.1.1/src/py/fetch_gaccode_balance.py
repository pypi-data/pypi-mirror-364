import requests
import schedule
import time
import datetime

from src.py.utils.constants import LOG_PATH, AUTH_TOKEN

# 请求 URL 和 headers
URL = "https://gaccode.com/api/credits/balance"
HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh",
    "Authorization": AUTH_TOKEN,
    "Content-Type": "application/json",
    "Referer": "https://gaccode.com/credits",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0"
}


def write_log(message):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(message + "\n")

def fetch_balance():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        response = requests.get(URL, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            log_message = f"[{now}] ✅ 200 OK - Response: {response.text}"
        elif response.status_code == 401:
            log_message = f"[{now}] ❌ 401 Unauthorized - Token may be expired"
        else:
            log_message = f"[{now}] ⚠️ {response.status_code} - Response: {response.text}"
    except Exception as e:
        log_message = f"[{now}] ❗ Exception occurred: {str(e)}"

    print(log_message)
    write_log(log_message)

def main():
    # 每 1 分钟执行一次
    minute = 1
    schedule.every(minute).minutes.do(fetch_balance)

    # 启动时立即执行一次
    fetch_balance()

    print(f"⏳ 定时任务已启动（每{minute}分钟执行一次），日志写入 {LOG_PATH}")
    while True:
        schedule.run_pending()
        time.sleep(10)

if __name__ == "__main__":
    main()
