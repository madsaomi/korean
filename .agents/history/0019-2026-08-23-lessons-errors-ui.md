# 0019: Уроки и страницы ошибок — финальный дизайн-проход

- **Дата/время (локальное):** 2026-08-23 13:20
- **Агент:** ox-alpha
- **Инициатор:** «продолжай улучшать и обновлять»
- **Коммит на момент начала:** 9edb909

## Что сделано

### Уроки (lessons/list.html)
- Бейджи: accent/soft вместо инлайн background.
- card-link/muted вместо инлайн color; описание урока — muted.

### Страницы ошибок (400/403/500.html)
- Эмодзи-иконки → bi-иконки: 🚫→shield-lock-fill, 🤔→question-circle,
  💥→exclamation-triangle-fill, 🏠→house-fill во всех трёх.
- Инлайн `style="color:var(--text-secondary)…"` → muted/small/d-block/mt-2.
- 404 уже был в стиле bi — не трогали.

## Проверка

- pytest → 125 passed; сканы mojibake/дублированных class-атрибутов → 0.
- Коммит d5f690a.

## Что осталось / передано дальше

Глубинка library: bookmarks/highlights/reader/search — типизированные,
требуют внимательного ручного прохода с учётом состояний.
