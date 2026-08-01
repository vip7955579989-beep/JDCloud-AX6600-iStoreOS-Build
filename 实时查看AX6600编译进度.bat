@echo off
title 雅典娜 AX6600 本地极速编译 - 实时日志监控窗口
color 0A
mode con cols=100 lines=32

echo ========================================================
echo   🚀 雅典娜 AX6600 本地极速编译 - 实时日志监控窗口
echo ========================================================
echo 正在实时打印 D:\AX6600_Build 编译日志流...
echo.

wsl -d Ubuntu-22.04 -u root bash -c "if [ -f /root/AX6600_Build/openwrt/build.log ]; then tail -f /root/AX6600_Build/openwrt/build.log; else watch -n 1 'ps aux | grep -E \"make|git|wget|gcc|g\+\+\"'; fi"
pause
