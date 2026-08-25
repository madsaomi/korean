# 0020: Библиотека — второй проход (bookmarks/search/highlights)

- **Дата/время (локальное):** 2026-08-23 14:00
- **Агент:** ox-alpha
- **Инициатор:** «продолжай» (библиотека)
- **Коммит на момент начала:** ca031d6

## Что сделано

### Библиотека
- **bookmarks.html**: title иконка в head убрана (было 🔖 → js-валидный text), header 🔖→bi-bookmark-fill, 🎨→bi-brush, green option внутри select: bi-phone→🟢 (color swatch), muted, badge.
- **search.html**: все `style="color:var(--text-secondary)"` → `.muted`; `background:var(--glass-bg)` на input → `glass-input`.
- **highlights.html**: header 🎨→bi-brush, muted.

### Сканы
- mojibake-скан всех шаблонов → 0; пароль-иконка и дубли class уже чисты с 0016.

## Проверка

- pytest → 125 passed
- Коммиты: 36e4516 (bookmarks), 3affd2f (search/highlights)

## Что осталось / передано дальше

Глубинка library: reader.html (крупный файл, ~15 инлайнов), detail.html дополнительные мелкие иконки (6 цветов) — низкий приоритет.
