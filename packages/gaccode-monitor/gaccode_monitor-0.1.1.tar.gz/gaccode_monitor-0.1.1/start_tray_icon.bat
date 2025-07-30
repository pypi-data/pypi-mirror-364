@echo off
cd /d "%~dp0"
echo 启动GACCode积分托盘图标...
.\.venv\Scripts\python.exe -m src.py.gaccode_tray_icon 