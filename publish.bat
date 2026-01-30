@echo off
chcp 65001 >nul
echo ========================================
echo    GitHub 发布助手
echo ========================================
echo.

echo 📋 发布前检查...
echo.

REM 检查 Git 是否安装
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到 Git，请先安装 Git
    echo    下载地址: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo ✓ Git 已安装
echo.

REM 检查是否已初始化
if not exist .git (
    echo 🔧 初始化 Git 仓库...
    git init
    echo ✓ Git 仓库初始化完成
    echo.
)

echo 📝 添加文件到暂存区...
git add .
echo ✓ 文件添加完成
echo.

echo 💬 请输入提交信息 (默认: Initial commit):
set /p commit_msg="> "
if "%commit_msg%"=="" set commit_msg=Initial commit: Telegram AI Bot v2.3.0

echo.
echo 📦 提交代码...
git commit -m "%commit_msg%"
echo ✓ 代码提交完成
echo.

echo ========================================
echo    下一步操作
echo ========================================
echo.
echo 1. 在 GitHub 创建新仓库
echo    访问: https://github.com/new
echo.
echo 2. 关联远程仓库
echo    git remote add origin https://github.com/你的用户名/telegram-ai-bot.git
echo.
echo 3. 推送代码
echo    git branch -M main
echo    git push -u origin main
echo.
echo ========================================

pause
