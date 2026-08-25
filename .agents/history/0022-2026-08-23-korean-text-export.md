# 0022: korean-text везде + экспорт прогресса JSON

- **Дата/время (локальное):** 2026-08-23 15:00
- **Агент:** ox-alpha
- **Инициатор:** «продолжай»
- **Коммит на момент начала:** 5219670

## Что сделано

### Корейский шрифт — класс вместо инлайнов
Все `style="font-family: 'Noto Sans KR', sans-serif;"` → `.korean-text`
(класс существовал с 0013). 9 шаблонов: breakdown, lessons/detail,
library/reader (частично — там CSS-переменная ридера, не тронуто),
vocabulary detail/list_detail/list_study/search/study/word.
Крупные слова карточек → `.korean-text.display-4`.

### Экспорт прогресса в JSON (UX из очереди)
`progress/views.py::progress_export` + URL `/progress/export/`:
- @login_required; attachment `klab-progress-YYYY-MM-DD.json`;
- полный дамп: профиль (уровень, стрик+заморозки, цели), ачивки, все слова
  (с категорией/интервалами/заметками), уроки, все попытки квизов;
- select_related по всем FK; ensure_ascii=False для читаемого корейского.
Кнопка «Экспорт JSON» в заголовке дашборда прогресса.

Smoke: 200 + слово и streak в теле; cleanup тестовых данных выполнен.

## Проверка

- pytest → 125 passed; ruff чисто; скан дублей class → 0.
- Коммит 11e2048 запушен.

## Что осталось / передано дальше

Инлайны ~200 (динамические width, reader CSS-var, conditional цвета) — точечно.
Очередь: тесты seed_data.
