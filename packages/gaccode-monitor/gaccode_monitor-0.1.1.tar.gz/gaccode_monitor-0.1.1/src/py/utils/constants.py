#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目常量定义
"""

import os
import configparser
from pathlib import Path

# 项目根目录 - 从当前文件向上4级
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
print("PROJECT_ROOT", PROJECT_ROOT)

# 日志路径
LOG_PATH = PROJECT_ROOT / "logs" / "fetch_gaccode_balance.log"
os.makedirs(PROJECT_ROOT / "logs", exist_ok=True)

# 配置文件路径
CONFIG_PATH = PROJECT_ROOT / "config.ini"

def get_token_from_config():
    """从配置文件获取token"""
    if not CONFIG_PATH.exists():
        # 创建默认配置文件
        config = configparser.ConfigParser()
        config['DEFAULT'] = {'token': ''}
        with open(CONFIG_PATH, 'w') as configfile:
            config.write(configfile)
        return ""
    
    # 尝试读取老格式配置（不带节的配置文件）
    try:
        with open(CONFIG_PATH, 'r') as f:
            content = f.read().strip()
            if content.startswith('token='):
                return content.split('=', 1)[1]
    except Exception:
        pass
    
    # 读取标准ini格式
    try:
        config = configparser.ConfigParser()
        config.read(CONFIG_PATH)
        return config.get('DEFAULT', 'token', fallback='')
    except Exception:
        return ""

# 从配置获取token
AUTH_TOKEN = get_token_from_config()
