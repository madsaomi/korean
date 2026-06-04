<div align="center">

# 🇰🇷 한글 K-lab

**Изучай корейский язык с нуля — бесплатно и в удобном темпе**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

</div>

---

## ✨ Возможности

| Раздел | Описание |
|--------|----------|
| **ㅎㅇ Хангыль** | Интерактивный алфавит с озвучкой и разбором предложений |
| **📚 Уроки** | Пошаговые курсы с прогрессом |
| **📖 Словарь** | Категории слов, флеш-карты, коллекции |
| **📝 Грамматика** | Правила с упражнениями |
| **🎯 Тесты** | Квизы с таймером и статистикой |
| **🔄 Повторение** | Система интервального повторения (SRS) |
| **🏆 Лидерборд** | Соревнуйся с другими учениками |
| **📊 Прогресс** | Heatmap стрика, графики результатов |
| **🎯 Дневные цели** | Отслеживай ежедневные задачи |

## 📸 Скриншоты

<div align="center">

![Dashboard](https://via.placeholder.com/800x400/6C5CE7/ffffff?text=Dashboard)
![Hangul](https://via.placeholder.com/800x400/667eea/ffffff?text=Hangul+Alphabet)
![Vocabulary](https://via.placeholder.com/800x400/764ba2/ffffff?text=Vocabulary+Cards)

</div>

## 🚀 Быстрый старт

### Требования

- Python 3.10+
- pip

### Установка

```bash
# Клонируй репозиторий
git clone https://github.com/your-username/k-lab.git
cd k-lab

# Создай виртуальное окружение
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate    # macOS/Linux

# Установи зависимости
pip install -r requirements.txt

# Примени миграции
python manage.py migrate

# Создай суперпользователя
python manage.py createsuperuser

# Запусти сервер
python manage.py runserver
```

Открой http://127.0.0.1:8000 в браузере.

## 🛠 Технологии

- **Backend:** Django 4.2, Python 3.10+
- **Frontend:** Bootstrap 5.3, Custom Glassmorphism CSS
- **БД:** SQLite (разработка) / PostgreSQL (продакшн)
- **Дополнительно:** Chart.js, Canvas Confetti, PWA (Service Worker)

## 📁 Структура проекта

```
k-lab/
├── accounts/       # Профиль, ачивки, дневные цели
├── core/           # Главная страница, поиск
├── grammar/        # Грамматика и упражнения
├── hangul/         # Алфавит, разбор предложений
├── lessons/        # Уроки и курсы
├── progress/       # Прогресс и статистика
├── quiz/           # Тесты и квизы
├── review/         # Повторение слов (SRS)
├── vocabulary/     # Словарь, категории, коллекции
├── templates/      # HTML-шаблоны
├── static/         # CSS, JS, медиа
├── manage.py
└── requirements.txt
```

## 📝 Лицензия

MIT License — используй свободно.

---

<div align="center">

Сделано с ❤️ для изучающих корейский

</div>
