#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目常量定义
"""

import os
from pathlib import Path

# 项目根目录 - 从当前文件向上4级
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
print("PROJECT_ROOT", PROJECT_ROOT)

# 日志路径
LOG_PATH = PROJECT_ROOT / "logs" / "fetch_gaccode_balance.log"
os.makedirs(PROJECT_ROOT / "logs", exist_ok=True)
