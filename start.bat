@echo off
chcp 65001 >nul
title K-Lab Notes Server

echo ======================================================
echo    🌸 K-Lab: Запуск базы заметок (Корейский + Японский)
echo ======================================================
echo.
echo Открытие сервера в браузере...
start http://127.0.0.1:8000/
echo.
echo Сервер запущен. Для остановки нажмите Ctrl+C.
echo.
.\venv\Scripts\python.exe -m mkdocs serve
pause
