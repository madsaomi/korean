# AGENTS.md

Инструкции для ИИ-агентов, работающих с этим репозиторием. Подробные доки лежат в `.agents/`:

| Файл | Что внутри |
|------|-----------|
| [`.agents/architecture.md`](.agents/architecture.md) | Структура проекта, приложения, модели, ключевые потоки данных |
| [`.agents/url-map.md`](.agents/url-map.md) | Карта всех HTML-маршрутов с пометками auth/POST |
| [`.agents/api-reference.md`](.agents/api-reference.md) | REST API: роуты, тела запросов, коды ответов |
| [`.agents/commands.md`](.agents/commands.md) | Окружение, тесты, миграции, сидирование |
| [`.agents/conventions.md`](.agents/conventions.md) | Правила кода, паттерны безопасности, что нельзя ломать |
| [`.agents/testing.md`](.agents/testing.md) | Как писать тесты (pytest-паттерны), дыры покрытия |
| [`.agents/known-issues.md`](.agents/known-issues.md) | Известные нереешённые проблемы (аудит от 2026-08) |
| [`.agents/history/`](.agents/history/INDEX.md) | Журнал работ агентов — append-only архив (см. правило 8) |
| [`.agents/HANDOFF.md`](.agents/HANDOFF.md) | Живая доска состояния: активная задача, что доделать (см. правило 9) |
| [`.agents/models-reference.md`](.agents/models-reference.md) | Шпаргалка по моделям и связям |

## Мультиагентный хэндофф

Проект настроен на передачу между разными агентами и инструментами
(opencode, Codex, Claude Code, Cursor, Gemini CLI). Точки входа:
`AGENTS.md` (Codex/opencode/Cursor), `CLAUDE.md` (Claude Code),
`GEMINI.md` (Gemini CLI) — все ведут сюда.

Протокол передачи (правило 9): перед остановкой обнови `.agents/HANDOFF.md`
(что сделано / следующий шаг / опасные места), завершённые задачи переноси
в журнал `.agents/history/`. Начинаешь сессию — первым делом читай HANDOFF.md.

## Краткая памятка

**Проект:** 한글 K-lab — Django-платформа для изучения корейского и японского.
**Стек:** Python 3.14, Django 5.x, DRF, SQLite, Bootstrap 5.3, pytest.
**Язык кода/комментариев:** английский; UI-строки и сообщения — русские.

### Обязательные правила

1. **Тесты только через pytest**: `.\venv\Scripts\python.exe -m pytest -q`
   (`manage.py test` находит 0 тестов — тесты используют pytest-фикстуры).
2. **Всегда запускай тесты и линтер** после изменений:
   `.\venv\Scripts\python.exe -m pytest -q` + `.\venv\Scripts\ruff.exe check .`,
   и `makemigrations --check`, если менял модели.
3. **Никаких raw SQL**, никакого `|safe` без nh3-санитизации, никаких `fields = '__all__'` в новых сериализаторах.
4. **Даты**: сравнение дат пользователя — только `timezone.localdate()`, не `timezone.now().date()` (UTC ≠ локальная зона).
5. **Пользовательские данные всегда фильтруй по `request.user`** (IDOR).
6. **Мультишаговые записи БД** оборачивай в `transaction.atomic()`.
7. **Не коммить без просьбы**, не меняй git-конфиг.
8. **Веди журнал работ** (`.agents/history/`): после любой содержательной задачи —
   новая запись по [_TEMPLATE.md](_TEMPLATE.md) + строка в [INDEX.md](_TEMPLATE.md).
   Формат: `NNNN-YYYY-MM-DD-slug.md`. **Append-only:** старые записи и строки
   INDEX никогда не изменяются; ошибки исправляются новой записью со ссылкой на ID.
   Следующий свободный номер смотри вверху INDEX.md.
9. **Протокол хэндоффа:** начинаешь сессию — прочитай [.agents/HANDOFF.md](.agents/HANDOFF.md)
   (активная задача, незавершённые шаги); останавливаешься — обнови его ДО потери
   контекста. Это единственный мутирующий файл документации.

### Быстрые команды

```powershell
.\venv\Scripts\python.exe -m pytest -q            # тесты (89 шт.)
.\venv\Scripts\python.exe manage.py migrate        # применить миграции
.\venv\Scripts\python.exe manage.py makemigrations # сгенерировать миграции
.\venv\Scripts\python.exe manage.py runserver      # дев-сервер
seed.bat                                           # полная установка с нуля
```
