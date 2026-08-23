# 0013: Редизайн страниц повторения

- **Дата/время (локальное):** 2026-08-23 09:00
- **Агент:** ox-alpha
- **Инициатор:** «продолжай» (дизайн-виток: review/vocabulary)
- **Коммит на момент начала:** 4ef98f8

## Что сделано

### review/index.html
- Исправлена семантика иконок оценок: «Легко» носила иконку телефона (наследие
  эмодзи-миграции 📲) → bi-lightning-charge-fill; «Снова» → bi-arrow-counterclockwise,
  «Нормально» → bi-hand-thumbs-up. Остаточные 🔴🟡 в кнопках заменены иконками.
- Классы оценок .btn-again/.btn-good/.btn-easy и .stat-* вместо инлайн border-color.
- 🃏 → bi-stack, 🔁 → bi-clock; .muted/.badge-accent/.glass-chip вместо инлайнов.

### review/flashcard.html
- Прогресс-бар сессии (#fc-progress): ширина = отвечено/всего, обновляется в
  showCard(); стартует с 0%.
- Те же семантичные кнопки оценок; чистка инлайнов (~12 → 5).

### CSS
- .btn-again/.btn-good/.btn-easy, .stat-again/.stat-good/.stat-easy,
  .session-progress (+.bar), .korean-text (Noto Sans KR), .glass-chip.

## Проверка

- pytest → 118 passed (JS-контракты review не менялись — только разметка).
- Инлайны: review/index 7, flashcard 5 (динамика/уникальные случаи).

## Что осталось / передано дальше

- Словарь (categories/detail/study) — следующий кандидат на тот же проход.
- Оставшиеся ~360 инлайн-стилей по проекту.
