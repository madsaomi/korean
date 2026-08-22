# Известные нерешённые проблемы

Остатки после аудита 2026-08 (исправлены все CRITICAL/HIGH и основные MEDIUM).
Брать отсюда, если нужен следующий шаг.

## LOW (сделать когда-нибудь)

1. **Self-XSS в конструкторе предложений** — `templates/hangul/builder.html`
   (`chip.innerHTML`, history из localStorage через `innerHTML`).
   Фикс: `textContent` / DOM API.
2. **Редиректы на сырой `HTTP_REFERER`** — `vocabulary/views.py`
   (add_to_review, save_word_note, word_list_add_word). Валидировать через
   `url_has_allowed_host_and_scheme()` или редиректить на именованный URL.
3. **Составные индексы library** — Bookmark/Highlight/Note фильтруются по
   `(user, language, slug)`, индекса нет (у ReadingProgress/LibraryTag — unique).
4. **Гонки сессии grammar exercises** — двойной сабмит двигает index на 2;
   ключи сессии не чистятся после результата; старт прохождения через GET.
5. **Дублирование списка ачивок** — dict в `accounts/views.py::achievements_page`
   vs `Achievement.ALL_CODES`. Источник один: модель.
6. **Фарминг**: пересдачи квиза безлимитны (ачивка «5 тестов» накручивается);
   повторения можно отвечать без проверки `next_review <= now`.
7. **`random_word_api`** — `order_by('?')`; при росте таблицы заменить на
   детерминированный выбор по дню как word_of_day.
8. **Service worker кэширует `/media/tts/*.mp3`** без вытеснения — `static/sw.js`.
9. **`lessons/tests.py` пустой**, критичная логика quiz_submit без тестов
   (серверный таймер, writing-ответы) — стоит покрыть.
10. **16 старых сериализаторов с `fields='__all__'`** — перечислить поля явно.

## Замечания по инфраструктуре

- `TokenAuthentication` включён в DRF, но `obtain_auth_token` не в urls — токен
  негде получить. Либо подключить `rest_framework.authtoken.views.obtain_auth_token`,
  либо выкинуть authtoken из INSTALLED_APPS.
- SQLite: `select_for_update()` фактически no-op между процессами; при переезде
  на PostgreSQL ничего менять не надо, но тестировать конкурентность нужно там.
- Кэш по умолчанию LocMemCache (в процессе): rate limit TTS и кэш учебника
  не шарятся между воркерами. Для прода — Redis.
- Нет CACHES/logging конфигурации в settings — добавить перед продом.
