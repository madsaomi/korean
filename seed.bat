@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
python manage.py seed_data
echo.
echo Учебник теперь читается напрямую из .md файлов.
echo Импорт больше не требуется.
pause
