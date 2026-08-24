<div align="center">

<img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI4MCIgaGVpZ2h0PSI4MCI+PGNpcmNsZSBjeD00MCBjeT00MCByPTM4IGZpbGw9IiM3ZjVhZjAiLz48dGV4dCB4PSI1MCIgeT0iNTQiIGZvbnQtc2l6ZT0iNDIiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZpbGw9IndoaXRlIiBmb250LWZhbWlseT0ic2Fucy1zZXJpZiI+SGFuPC90ZXh0Pjwvc3ZnPg==" width="80" alt="한글 K-lab">

# 한글 K-lab

**Учим корейский и японский с нуля — бесплатно и в своём темпе**

Интерактивная платформа: алфавит с озвучкой, словарь с интервальным повторением,
тесты, учебник из двух языков — в одном glassmorphism-интерфейсе.

[![CI](https://github.com/madsaomi/korean/actions/workflows/ci.yml/badge.svg)](https://github.com/madsaomi/korean/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.x-092E20?style=flat&logo=django&logoColor=white)](https://djangoproject.com)
[![Tests](https://img.shields.io/badge/tests-125%20passing-00b894)](#-запуск)
[![License](https://img.shields.io/badge/License-MIT-fdcb6e)](LICENSE)

</div>

---

## ✨ Возможности

| | Раздел | Что внутри |
|---|--------|-----------|
| 🔤 | **Алфавит** | Интерактивный хангыль с TTS-озвучкой, разбор предложений, конструктор фраз |
| 📚 | **Словарь** | Категории слов, режим заучивания, личные коллекции, CSV-экспорт |
| 🔄 | **Повторение (SRS)** | Интервальное повторение: лестница интервалов, заморозки серии ❄️, флеш-режим с горячими клавишами |
| 🎯 | **Тесты** | Квизы с серверным таймером, разбор ошибок с объяснениями, уровни сложности |
| 📖 | **Грамматика** | Темы → правила с формулами и примерами + тренажёр упражнений |
| 📘 | **Учебник** | Корейский 🇰🇷 и японский 🇯🇵 курсы: оглавление, закладки, выделения 6 цветов, заметки, теги, поиск по тексту |
| 🏆 | **Мотивация** | Стрики, ачивки, дневные цели, лидерборд, heatmap активности |
| 📊 | **Прогресс** | Статистика уроков/слов/тестов, графики результатов |
| 📱 | **PWA** | Установка на устройство, офлайн-режим, тёмная тема |

## 🚀 Запуск

```bash
git clone https://github.com/madsaomi/korean.git
cd korean

python -m venv venv
venv\Scripts\activate            # Windows
# source venv/bin/activate       # macOS/Linux

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Открой <http://127.0.0.1:8000> — готово.

> 💡 Тесты: `pytest -q` · Линтер: `ruff check .` · Полная установка скриптом: `seed.bat`

## ⚙️ Конфигурация

Все переменные окружения — необязательные, см. [`.env.example`](.env.example):

```ini
DJANGO_DEBUG=False                    # прод-режим (HSTS, secure cookies, SSL redirect)
DJANGO_SECRET_KEY=...                 # обязателен при DEBUG=False
DB_ENGINE=postgres                    # PostgreSQL вместо SQLite
REDIS_URL=redis://localhost:6379/1    # общий кэш между воркерами
```

## 🛠 Технологии

| Слой | Стек |
|------|------|
| Backend | Python 3.14, Django 5.x, DRF |
| Frontend | Bootstrap 5.3, Bootstrap Icons, glassmorphism-CSS, Chart.js |
| Данные | SQLite / PostgreSQL, Redis (кэш) |
| Инфраструктура | WhiteNoise, gunicorn, GitHub Actions (ruff + pytest) |
| Контент | Markdown-учебники с YAML-frontmatter + nh3-санитизация |

## 📁 Структура

```
korean/
├── accounts/       # Профиль, ачивки, стрики, заморозки ❄
├── api/            # REST API (DRF): слова, квизы, прогресс, закладки
├── config/         # Settings, .env-лоадер, WSGI/ASGI
├── core/           # Главная, поиск, лидерборд, streak-middleware
├── grammar/        # Темы, правила, упражнения
├── hangul/         # Алфавит, TTS-озвучка, разбор предложений
├── lessons/        # Курсы и уроки
├── library/        # Учебники ko+ja: чтение, закладки, выделения
├── progress/       # Статистика и дашборд прогресса
├── quiz/           # Тесты с серверным таймером
├── review/         # SRS-движок (services.py — единая точка логики)
├── vocabulary/     # Слова, категории, коллекции
├── templates/      # Шаблоны (glassmorphism + тёмная тема)
├── static/         # CSS/JS, service worker, manifest
├── Корейский/      # Исходники учебника 🇰🇷 (markdown)
└── Японский/       # Исходники учебника 🇯🇵 (markdown)
```

## 🧪 Для ИИ-агентов

Репозиторий настроен для работы любых ИИ-агентов (opencode, Codex,
Claude Code, Cursor, Gemini CLI):

- [`AGENTS.md`](AGENTS.md) — точка входа: правила, команды, индекс документации
- [`.agents/HANDOFF.md`](.agents/HANDOFF.md) — живое состояние проекта
- [`.agents/history/`](.agents/history/INDEX.md) — журнал работ агентов (18 записей)

## 📦 Деплой

Пошаговый чеклист — [`DEPLOY.md`](DEPLOY.md):
gunicorn + nginx, PostgreSQL и Redis через переменные окружения,
`manage.py check --deploy` проходит без замечаний.

## 📝 Лицензия

MIT — см. [LICENSE](LICENSE).

---

<div align="center">

Сделано с ❤️ для изучающих 한국어 и 日本語

</div>
