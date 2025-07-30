import json
import requests
import threading
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import pystray
from pystray import MenuItem as item

from src.py.utils.constants import LOG_PATH, PROJECT_ROOT, AUTH_TOKEN

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

# 全局变量存储余额数据
balance_data = {
    "balance": 0,
    "creditCap": 0,
    "refillRate": 0,
    "lastRefill": ""
}

def create_image(balance=0, credit_cap=0):
    """创建显示余额的图像 - 类似任务管理器的竖向水槽"""
    # 创建一个 32x64 的透明图像 (竖向长方形)
    width = 32
    height = 64
    image = Image.new('RGBA', (width, height), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # 计算余额百分比
    percentage = min(100, int(balance / credit_cap * 100)) if credit_cap > 0 else 0
    
    # 绘制长方形边框 (2像素宽)
    border_color = (180, 180, 180, 255)  # 灰色边框
    draw.rectangle([(0, 0), (width-1, height-1)], fill=None, outline=border_color, width=2)
    
    # 内部填充区域
    inner_margin = 4
    inner_width = width - (inner_margin * 2)
    inner_height = height - (inner_margin * 2)
    
    # 绘制背景 (深色)
    background_color = (50, 50, 50, 200)  # 深灰色背景
    draw.rectangle([(inner_margin, inner_margin), 
                   (width-inner_margin-1, height-inner_margin-1)], 
                   fill=background_color)
    
    # 计算水槽高度 (百分比反向，从底部往上填)
    water_height = int((percentage / 100) * inner_height)
    water_top = height - inner_margin - water_height
    
    # 绘制蓝色水槽
    # 根据百分比调整颜色 - 低时为红色，中等为黄色，高时为蓝色
    if percentage > 70:
        water_color = (0, 120, 255, 220)  # 蓝色
    elif percentage > 30:
        water_color = (255, 200, 0, 220)   # 黄色
    else:
        water_color = (255, 60, 60, 220)   # 红色
        
    if water_height > 0:
        draw.rectangle([
            (inner_margin, water_top),
            (width-inner_margin-1, height-inner_margin-1)
        ], fill=water_color)
    
    return image

def fetch_balance():
    """获取GACCode的积分余额"""
    global balance_data
    try:
        response = requests.get(URL, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            # 更新全局数据
            balance_data = json.loads(response.text)
            return balance_data
        else:
            print(f"请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"发生异常: {str(e)}")
    return None

def update_icon(icon):
    """更新系统托盘图标"""
    global balance_data
    while True:
        new_data = fetch_balance()
        if new_data:
            # 更新图标
            icon.icon = create_image(new_data["balance"], new_data["creditCap"])
            # 更新提示文本
            icon.title = f"GACCode 积分: {new_data['balance']}/{new_data['creditCap']} ({int(new_data['balance']/new_data['creditCap']*100)}%)"
        
        # 每分钟更新一次
        time.sleep(60)

def read_last_log():
    """读取最后一行日志来获取余额信息"""
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1].strip()
                # 尝试解析JSON部分
                try:
                    json_start = last_line.find('{"balance":')
                    json_end = last_line.rfind('}') + 1
                    if json_start != -1 and json_end != -1:
                        json_str = last_line[json_start:json_end]
                        data = json.loads(json_str)
                        return data
                except:
                    pass
    except Exception as e:
        print(f"读取日志失败: {str(e)}")
    return None

def exit_action(icon):
    icon.stop()

def setup_tray():
    # 初始化余额数据（尝试从日志中读取）
    global balance_data
    log_data = read_last_log()
    if log_data:
        balance_data = log_data
    
    # 创建初始图标
    image = create_image(balance_data["balance"], balance_data["creditCap"])
    
    # 创建系统托盘图标
    icon = pystray.Icon(
        "gaccode_balance",
        image,
        f"GACCode 积分: {balance_data['balance']}/{balance_data['creditCap']}",
        menu=pystray.Menu(
            item('退出', exit_action)
        )
    )
    
    # 启动更新线程
    threading.Thread(target=update_icon, args=(icon,), daemon=True).start()
    
    # 运行托盘图标
    icon.run()

if __name__ == "__main__":
    setup_tray() 