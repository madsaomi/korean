# Архитектура

Django-монолит для изучения корейского (ko) и японского (ja). Шаблонный рендеринг
(Bootstrap 5.3 + кастомный glassmorphism CSS) и REST API на DRF рядом.

## Приложения

| App | Назначение | Ключевые модели |
|-----|-----------|-----------------|
| `accounts` | Профиль, ачивки, стрики, дневные цели | `UserProfile`, `Streak`, `Achievement`, `DailyGoal` |
| `core` | Главная, поиск, leaderboard, middleware | — |
| `hangul` | Алфавит, разбор предложений, конструктор, TTS-озвучка | без моделей |
| `vocabulary` | Слова, категории, коллекции пользователя | `Category`, `Word`, `WordList` |
| `grammar` | Темы/правила/упражнения грамматики | `GrammarTopic`, `GrammarRule`, `GrammarExercise` |
| `lessons` | Курсы и уроки | `Course`, `Lesson`, `LessonStep` |
| `quiz` | Тесты с таймером | `Quiz`, `Question`, `Answer` |
| `progress` | Прогресс пользователя | `UserLessonProgress`, `UserWordProgress`, `UserQuizResult` |
| `review` | SRS-повторение слов | без моделей (пишет в `UserWordProgress`) |
| `library` | Учебники ko+ja из markdown-файлов: закладки, выделения, заметки, теги | `ReadingProgress`, `Bookmark`, `Highlight`, `Note`, `LibraryTag` |
| `api` | DRF-эндпоинты ко всему выше | сериализаторы поверх чужих моделей |

## Потоки данных

### Прогресс слова (SRS)
```
review/views.py → review/services.py::apply_review()
  └─ UserWordProgress (user+word unique): review_count, next_review, learned
  └─ после save → accounts/utils.py::check_word_achievements()
```
Лестница интервалов: again → сброс счётчика + 10 мин (learned слово при провале
снимается с learned — возврат в активную ротацию); good → [1, 3, 7, 14, 30] дней
(learned статус сохраняется); easy → learned=True + 7 дней. Очереди повторения
фильтруются только по `next_review <= now` БЕЗ фильтра learned — выученные слова
возвращаются на повторение по расписанию (retention loop). Антифарминг:
apply_review отклоняет слово раньше срока (WordNotDue, грейс 5 сек).
Логика живёт ТОЛЬКО в `apply_review` — HTML-вьюхи и API её переиспользуют,
дублировать нельзя.

### Учебник (library)
Markdown-файлы лежат в `Корейский/` и `Японский/` (frontmatter YAML + body).
`library/pages.py` парсит всё при старте и кэширует 10 минут (Django cache).
Рендер: markdown → свои постпроцессоры (id заголовков, TTS-спаны) → **nh3-санитизация**.
Пользовательские данные (закладки/выделения) — в моделях с ключом `(user, language, slug)`.

### Ачивки и стрик
`core/middleware.py::StreakMiddleware` раз в день обновляет стрик и дёргает проверки
ачивок (`accounts/utils.py`). Ачивка = строка `Achievement(user, code)` с уникальным кодом.

Заморозки серии: `Streak.freezes` (макс. `MAX_FREEZES=3`). Пропущен ровно 1 день +
есть заморозка → серия сохраняется и растёт как обычно, заморозка списывается
(сообщение пользователю). Каждые 7 дней стрика выдаётся +1 заморозка.
Пропуск 2+ дней — сброс на 1 без спасения (см. тесты core/tests.py).

## Настройки

`config/settings.py`: DEBUG по умолчанию True; при DEBUG=False обязателен
env `DJANGO_SECRET_KEY` (иначе RuntimeError), включаются HSTS/secure cookies/SSL redirect.
DRF: SessionAuth + TokenAuth, throttle anon 100/day / user 1000/hour, пагинация 50.

## Тесты

pytest + pytest-django, фикстуры лежат в `tests.py` каждого приложения
(`conftest.py` нет — общих фикстур нет, каждая тестирующая фабрика локальная).
`manage.py test` не работает (находит 0 тестов) — только pytest.
