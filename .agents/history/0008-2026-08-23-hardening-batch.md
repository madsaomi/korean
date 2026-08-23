# 0008: Hardening-батч — env, редиректы, XSS, каталог ачивок, тесты

- **Дата/время (локальное):** 2026-08-23 05:30
- **Агент:** ox-alpha
- **Инициатор:** «продолжай» (по очереди из HANDOFF)
- **Коммит на момент начала:** 145527c

## Что сделано

### Инфраструктура
- `.env.example` — документированы DJANGO_SECRET_KEY/DEBUG/ALLOWED_HOSTS/
  CSRF_TRUSTED_ORIGINS (+пометка, что Django сам .env не читает).
- `config/settings.py`: CSRF_TRUSTED_ORIGINS из env; SECURE_PROXY_SSL_HEADER при DEBUG=False.
- collectstatic выполнен локально — WhiteNoise-ворнинг исчез.

### Безопасность / качество (known-issues)
- **#1 self-XSS** в `templates/hangul/builder.html`: chip и история предложений
  переведены с innerHTML на DOM API (createTextNode/textContent).
- **#2 referer-редиректы**: `_safe_referer_redirect()` в vocabulary/views.py —
  проверка `url_has_allowed_host_and_scheme`, 6 мест заменены.
- **#5 ачивки**: единый источник правды `Achievement.CATALOG` (code → icon/title/
  description); grant_achievement(user, code) берёт тексты оттуда; middleware и
  achievements_page используют каталог. Дублированные списки удалены.
- **#7 random_word_api**: вместо ORDER BY RANDOM — COUNT + индексированный offset.
- **#8 service worker**: отдельная ветка для `/media/` (cache-first, как static).

### Тесты (+18, всего 107)
- `review/tests.py` (был пустым): лестница SRS — again сбрасывает, good шаги
  1д→кап 30д, easy learned+ачивка ten_words на пороге, невалидный action,
  pending_review_count.
- `quiz/tests.py`: серверный таймер — без старта отклоняется, после GET принимается,
  просроченная попытка не записывается, quiz без лимита не требует старта;
  writing «4» сравнивается текстом; нормализация регистра/пробелов.
- `accounts/tests.py`: daily_goals GET/POST/невалидный ввод (регрессия на баг
  DailyGoal из 0006), соответствие CATALOG ↔ ALL_CODES на странице ачивок.

## Проверка

- pytest → 107 passed, warnings: 0 (staticfiles собран).
- ruff check . → чисто (4 автофикса импортов).
- Коммит ea5e640 "feat: hardening batch...".

## Что осталось / передано дальше

known-issues.md переписан: остались library-индексы, grammar-сессии,
фарминг-лимиты, fields='__all__', пустой lessons/tests.py + инфраструктура.
