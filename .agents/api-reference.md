# REST API (DRF)

База: `/api/`, роутер DefaultRouter (`api/urls.py`). Аутентификация: сессионная
(CSRF обязателен). TokenAuthentication объявлен в settings, но токены фактически
не выдаются.
Глобально: `IsAuthenticatedOrReadOnly`, throttle anon 100/day, user 1000/hour,
пагинация 50 (`?page=`), фильтры django-filter + SearchFilter + OrderingFilter.

## Read-only каталоги (аноним — чтение)

| Роут | Фичи |
|------|------|
| `/api/vocabulary/categories/` | lookup `slug`; `words_count` (аннотация) |
| `/api/vocabulary/words/` | filterset `category, level, category__slug`; search `korean, russian, romanization`; ordering `korean, level, created_at` |
| `/api/lessons/courses/` | filterset `level`; `lessons_count` |
| `/api/lessons/lessons/` | list без steps, detail со steps |
| `/api/grammar/topics/` | lookup `slug`; вложенные rules; `rules_count` |
| `/api/grammar/exercises/` | filterset `topic, difficulty, topic__slug` |
| `/api/quiz/` | **ответы без `is_correct`/`explanation`** — не возвращать их обратно |

## Пользовательские (IsAuthenticated)

### `/api/progress/`
- `GET overview/` → `{streak, goal, stats{words_learned, quizzes_taken, lessons_completed, avg_quiz_score}}`
- `GET words/ | quizzes/ | lessons/ | achievements/` — пагинированные списки

### `/api/review/`
- `GET /api/review/` — очередь до 20 due-слов
- `POST /api/review/` `{word_id: int, action: "again"|"good"|"easy"}` → 200
  `{success, action, learned, next_review}`; 404 если слова нет в прогрессе;
  400 при невалидном action или если слово ещё не due (антифарминг,
  грейс 5 сек). Логика — только через `review/services.py::apply_review`.

### `/api/library/`
Пагинации нет (сознательно). Все записи скоупятся по request.user.
`language` берётся из body/query (`ko`|`ja`, default `ko`, невалидный → 400).

| Метод+экшен | Тело / ответ |
|---|---|
| `GET /api/library/` | `{reading_slugs: [...]}` |
| `GET\|POST progress/` | POST `{slug, read?, language?}` → объект ReadingProgress (upsert) |
| `GET\|POST\|DELETE bookmarks/` | POST `{slug, title?, anchor?, note?, language?}` — идемпотентно (get_or_create): 201 новый / 200 существующий. DELETE `?id=` → 204\|404 |
| `GET\|POST\|DELETE notes/` | POST требует `content` (400 иначе); заметок может быть много |
| `GET\|POST tags/` | POST `{slug, tag}` — get_or_create по `(user, language, slug, tag)` |

### `/api/auth/`
- `GET /api/auth/` — текущий User
- `GET profile/` — профиль (+get_or_create)
- `/api/auth/login/`, `/api/auth/logout/` из rest_framework.urls (сессионная форма)

Токены: `POST /api/token-auth/` с `{username, password}` → `{token}`.
Дальше заголовок `Authorization: Token <token>`.

## Правила при изменении API

1. Новые пользовательские эндпоинты: `permission_classes = [IsAuthenticated]`
   явно, не полагаться на глобальный OrReadOnly.
2. POST-тела валидировать (сериализатор или явные проверки) — клиент получает 400,
   а не 500.
3. Поля ответа с count'ами читать из аннотаций queryset'а ViewSet
   (см. `get_*_count` в serializers.py), не добавлять `obj.related.count()` в цикле.
4. Изменения контракта review/library отражай и в `.agents/url-map.md`.
