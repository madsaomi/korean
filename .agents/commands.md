# Окружение и команды

Windows, PowerShell. Python 3.14, venv лежит в `venv\` (не в git).

## Установка с нуля

```powershell
python -m venv venv
.\venv\Scripts\pip.exe install -r requirements.txt
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py createsuperuser
```
Или целиком: `seed.bat`.

## Ежедневные команды

```powershell
.\venv\Scripts\python.exe -m pytest -q              # тесты — ВСЕГДА после правок
.\venv\Scripts\python.exe manage.py runserver       # дев-сервер на :8000
.\venv\Scripts\python.exe manage.py makemigrations  # после изменений моделей
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py makemigrations --check   # CI-проверка дрейфа моделей
```

## Сервисные

```powershell
# Очистка кэша TTS-файлов старше N дней (сначала dry-run)
.\venv\Scripts\python.exe manage.py cleanup_tts --days=7 --dry-run
.\venv\Scripts\python.exe manage.py cleanup_tts --days=7
```

## Проверки перед завершением задачи

1. `pytest -q` — зелёный (89 тестов на момент аудита).
2. Менял модели? → миграция создана и `makemigrations --check` молчит.
3. `manage.py check` без ошибок.

## Нюансы окружения

- `manage.py test` НЕ работает: тесты pytest-стиля с фикстурами. Только `-m pytest`.
- Глобального Django нет — только через `.\venv\Scripts\python.exe`.
- Без `DJANGO_DEBUG=False` секретный ключ генерируется случайным при каждом старте
  (сессии слетают) — это нормально для разработки.
- Кэш учебника живёт 10 минут; правки md в `Корейский/`/`Японский/` подтянутся не сразу.
