# Деплой-чеклист

Целевая схема: Linux + gunicorn + nginx (или любой reverse-proxy) + PostgreSQL + Redis.

## 1. Зависимости и код

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements-prod.txt   # включает gunicorn, psycopg, django-redis
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## 2. Переменные окружения (обязательные)

| Переменная | Значение |
|---|---|
| `DJANGO_DEBUG` | `False` — иначе сервер не примет прод-конфиг |
| `DJANGO_SECRET_KEY` | длинная случайная строка (`python -c "import secrets; print(secrets.token_urlsafe(50))"`) |
| `DJANGO_ALLOWED_HOSTS` | твой домен через запятую |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://твой-домен` |

Опциональные:
- `DB_ENGINE=postgres` + `DB_NAME/DB_USER/DB_PASSWORD/DB_HOST/DB_PORT`
  (без них — SQLite в корне проекта)
- `REDIS_URL=redis://localhost:6379/1` — общий кэш между воркерами
  (rate limit TTS, кэш учебника). Без него — LocMemCache на процесс.
- `DJANGO_LOG_LEVEL` (по умолчанию INFO)

`.env` в корне подхватывается автоматически; реальные переменные окружения
имеют приоритет. `.env` не коммитится.

## 3. Запуск gunicorn

```bash
gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3 --timeout 60
```

Через systemd-юнит: WorkingDirectory=корень проекта,
ExecStart=`venv/bin/gunicorn ...`, Restart=always.

## 4. nginx

```nginx
server {
    listen 443 ssl;
    server_name your.domain;

    location /static/ { alias /path/to/korean/staticfiles/; }
    location /media/  { alias /path/to/korean/media/; }      # tts mp3
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto https;
    }
}
```

`X-Forwarded-Proto https` обязателен: при DEBUG=False Django читает его через
SECURE_PROXY_SSL_HEADER. HTTPS нужен для HSTS/secure cookies, которые включаются
автоматически при DEBUG=False.

## 5. Периодические задачи

- Очистка TTS-кэша: cron раз в сутки
  `python manage.py cleanup_tts --days=7`

## 6. После деплоя проверить

- [ ] `https://домен/admin/` открывается, статика сжатая (whitenoise)
- [ ] Регистрация/логин работают (CSRF за прокси = заголовок из п.4)
- [ ] TTS-озвучка отвечает (rate limit по IP через Redis)
- [ ] Учебник открывается, закладки/выделения сохраняются
- [ ] `python manage.py check --deploy` без критичных замечаний
