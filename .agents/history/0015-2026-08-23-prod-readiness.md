# 0015: Прод-подготовка

- **Дата/время (локальное):** 2026-08-23 10:00
- **Агент:** ox-alpha
- **Инициатор:** «что там по плану?» → согласие на прод-подготовку
- **Коммит на момент начала:** 4587394

## Что сделано

### .env-лоадер без зависимостей
- `config/env_loader.py::load_dotenv()`: KEY=VALUE, комментарии, export-префикс,
  кавычки; существующие переменные окружения имеют приоритет.
- Подключён в settings.py до чтения любых env (BASE_DIR/.env).
- Тесты `config/tests.py` (+5): парсинг, кавычки, экспорт, приоритет env,
  отсутствие файла.

### Env-переключатели инфраструктуры
- `DB_ENGINE=postgres` + DB_NAME/USER/PASSWORD/HOST/PORT → PostgreSQL
  (без них — SQLite как раньше).
- `REDIS_URL` → django_redis.RedisCache (общий кэш между воркерами);
  без него — явный LocMemCache.
- `SECURE_HSTS_PRELOAD = True` при DEBUG=False: теперь `check --deploy`
  показывает НОЛЬ предупреждений безопасности с валидным ключом
  (проверено с DJANGO_DEBUG=False + сильным ключом).

### requirements-prod.txt
gunicorn, psycopg[binary] 3, django-redis. Локальный dev не тянет их.

### DEPLOY.md
Чеклист: зависимости, обязательные/опциональные env, gunicorn-команда,
nginx-конфиг с X-Forwarded-Proto, cron для cleanup_tts, пост-деплой проверки.

### .env.example дополнен
DB_ENGINE/REDIS_URL блоки.

## Проверка

- pytest → 123 passed (118 + 5 новых); ruff чисто (2 автофикса); check чисто;
- check --deploy (DEBUG=False, сильный ключ) → 0 warnings.

## Что осталось / передано дальше

Реальный деплой на сервер — вне репозитория. Из очереди HANDOFF остались:
дизайн quiz/library/grammar, streak-freeze, тесты seed_data.
