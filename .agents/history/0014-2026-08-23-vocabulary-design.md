# 0014: Дизайн-проход по словарю

- **Дата/время (локальное):** 2026-08-23 09:45
- **Агент:** ox-alpha
- **Инициатор:** «продолжай»
- **Коммит на момент начала:** fe3498c

## Что сделано

### CSS
- Новый класс `.glass-pill` (border-radius 50px + паддинги) — заменяет
  повторяющийся инлайн-стиль пилюль-контейнеров в study/list_study/study_custom.

### Шаблоны vocabulary
- `categories.html`: 🏷️ → bi-tags-fill, card-link/muted вместо инлайнов.
- `study_custom.html`: 📂 → bi-folder, 🚀 → bi-rocket-takeoff-fill,
  👆 → bi-hand-index; шрифт корейского → .korean-text (display-4);
  бейджи → badge-accent/badge-soft; muted вместо color-инлайнов.
  Инлайнов: 12 → 7 (динамический width прогресса и max-width остались).
- `study.html`, `list_study.html`: pill-класс применён.

## Проверка

- pytest → 118 passed; скан на дублированные class-атрибуты и mojibake → 0.
  Попутно поймал собственный косяк: bulk-replace создал двойной class="..."
  в одном <p> — исправлен до коммита (de35a42).

## Что осталось / передано дальше

- Оставшиеся инлайн-стили проекта (~350): точечно при касании файлов.
- Прод-подготовка из HANDOFF (Redis/environ/PostgreSQL) — не начиналась.
