# 0016: Дизайн-проход quiz + grammar + profile

- **Дата/время (локальное):** 2026-08-23 10:45
- **Агент:** ox-alpha
- **Инициатор:** «продолжай улучшать и обновлять»
- **Коммит на момент начала:** f6d060e

## Что сделано

### Quiz (0abcef1)
- Фильтры уровней → bi-1/2/3-circle (были 🟡🔴 и bi-phone у «С нуля»);
- ⏱ → bi-stopwatch; бейджи → badge-accent/badge-soft/badge-soft-red;
- Результат: yesno-эмодзи (🎉,😅) → bi-emoji-laughing/neutral-fill;
- korean-text для вопросов, muted вместо инлайнов.

### Grammar + Profile (c344576)
- grammar list/detail: card-link/muted/badge-классы, korean-text для примеров,
  aria-label на TTS-кнопках.
- profile.html: 📈 → bi-graph-up, градиентный бейдж уровня → .badge-gradient,
  Chart.js запинен на 4.4.1 с вычисленным SRI; .badge-pass/.badge-fail
  для истории тестов; иконка пароля bi-key-fill (был login-значок).

### Фикс собственного косяка (8a6af40)
- Bulk-replace `style="color: var(--text-secondary);"` → `class="muted"`
  создал 3 дублированных class-атрибута в profile.html (первый скан дал ложные
  срабатывания из-за жадного паттерна по вложенным тегам). Строгий паттерн
  `class="[^"]*"\s+class=` нашёл реальные, все объединены. Вывод в журнал:
  после bulk-замен гнать строгий скан на дубли атрибутов.

## Проверка

- pytest → 118 passed; строгий скан дублированных class-атрибутов по всем
  шаблонам → 0.
- Коммиты: 0abcef1, c344576, 8a6af40.

## Что осталось / передано дальше

Дизайн-проходами покрыты: главная, review×2, vocabulary, quiz, grammar,
accounts/profile. Не пройдены: library (крупный), hangul, lessons, ошибки 4xx.
