@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
python manage.py seed_data
python manage.py import_library
python manage.py import_library --language ja
pause
