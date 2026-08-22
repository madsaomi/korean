# Конвенции и паттерны безопасности

Итог аудита 2026-08: критичные дыры закрыты. Новые изменения не должны их вернуть.

## Обязательные правила

1. **IDOR**: любые пользовательские данные — только через `filter(user=request.user)`
   или `get_object_or_404(Model, pk=pk, user=request.user)`. Никаких «просто pk».
2. **Транзакции**: несколько связанных записей (прогресс + ачивки + результаты)
   — `transaction.atomic()`. SRS-запись — через `review/services.py::apply_review`
   (там уже atomic + select_for_update). Не дублировать логику.
3. **Даты пользователя**: `timezone.localdate()` для сравнения с `__date`/TruncDate/
   DateField. `timezone.now().date()` даёт UTC-дату и ломает границы дня
   (таймзона Asia/Tashkent = UTC+5).
4. **XSS**: автоэкранирование не отключать. Markdown рендерить только через
   `library/views.py::_process_md_html` (nh3 в конце). В шаблонах `|safe` — только
   на выходе этой функции (`html_content`). Данные для JS — через `json_script`.
5. **Сериализаторы DRF**: поля перечислять явно, `fields='__all__'` запрещён в новом
   коде (в старых 16 сериализаторах остаётся до рефакторинга). Пользовательский ввод —
   через сериализатор или явную валидацию, сырой `request.data` → 400, не 500.
6. **Raw SQL запрещён**. ORM покрывает всё; LIKE-wildcard из пользовательского ввода
   вырезать: `value.replace('%','').replace('_','')`.
7. **Гонки**: toggle-паттерны (создать/удалить) — только с UniqueConstraint +
   обработка IntegrityError. Счётчики — `F()`-выражения или select_for_update.

## Стиль

- Код и комментарии — английский; строки UI, сообщения messages/JsonResponse — русский.
- Views тонкие; переиспользуемая бизнес-логика — в `services.py` приложения.
- Мутации — `@require_POST` / `methods=['post']`; GET не меняет состояние
  (исключение сейчас: grammar start_exercise, см. known-issues).
- Модели: у пользовательских таблиц — unique_together/constraints; под частые фильтры
  — составные индексы (пример: `UserWordProgress(user, learned, next_review)`).
- Тесты: pytest-фикстуры рядом с тестируемым кодом в `tests.py`.

## Что нельзя ломать

- Контракт JSON ответов повторений: `{success, action?, learned?, next_review?,
  pending_count?}` — шаблоны `templates/review/*.html` на него завязаны.
- Формат имени TTS-файла: HMAC-SHA256(SECRET_KEY, text)[:32] + `.mp3` — путь строится
  из хэша, пользовательский текст в путь не попадает.
- Публичность страниц учебника/алфавита для анонимов (TTS API тоже публичный,
  защищён rate limit'ом по IP).
- Кастомные обработчики ошибок 400/403/404/500 в `config/urls.py` + `ErrorPageMiddleware`.
