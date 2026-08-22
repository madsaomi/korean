# Карта URL

Префиксы подключены в `config/urls.py`. 🔒 = требует логина, POST-эндпоинты
помечены `POST`. Полный список имён — в `*/urls.py` каждого приложения.

## Публичные страницы (аноним ок)

| URL | name | Что там |
|-----|------|---------|
| `/` | `index` | главная; падает с 500, если сломать контекст word_of_day |
| `/search/?q=` | `unified_search` | поиск по словам/грамматике/урокам |
| `/leaderboard/` | `leaderboard` | топы стриков/уроков/тестов |
| `/random-word/` | `random_word_api` | JSON случайного слова |
| `/hangul/`, `/hangul/breakdown/`, `/hangul/builder/` | `hangul*` | алфавит, разбор, конструктор |
| `/hangul/tts/?text=` | `tts_audio` | GET JSON mp3-url; rate limit 30/мин на IP, 502 при сбое gTTS |
| `/vocabulary/`, `/vocabulary/search/`, `/vocabulary/study/` | `category_list`, `word_search`, `study_custom` | словарь и режим заучивания |
| `/vocabulary/<slug>/`, `/vocabulary/<slug>/study/`, `/vocabulary/word/<pk>/` | `category_detail`, `study_category`, `word_detail` | категории и карточка слова |
| `/lessons/` | `lesson_list` | список курсов |
| `/grammar/`, `/grammar/<slug>/`, `/grammar/exercises/` | `grammar_list`, `grammar_detail`, `exercise_list` | грамматика |
| `/quiz/`, `/quiz/<pk>/` | `quiz_list`, `quiz_detail` | тесты; GET detail пишет старт таймера в сессию |
| `/library/` | `library_home` | выбор языка учебника |
| `/library/korean/...`, `/library/japanese/...` | `library_{ko\|ja}_*` | index/random/search/bookmarks/highlights/reader/`<slug>` |

## Личные страницы (🔒)

| URL | name |
|-----|------|
| `/accounts/register/` (публичный), `/accounts/login/`, `/accounts/logout/` | `register`, `login`, `logout` |
| `/accounts/profile/`, `profile/edit/`, `password/`, `achievements/`, `goals/` | `profile`, `edit_profile`, `change_password`, `achievements`, `daily_goals` |
| `/lessons/<course_id>/[<lesson_id>/]` | `lesson_detail` |
| `/grammar/exercises/start|do|result/` | `start_exercise`, `do_exercise`, `exercise_result` |
| `/review/`, `/review/flashcard/` | `review`, `flashcard` — POST принимают form или JSON `{word_id, action}` |
| `/progress/` | `progress_dashboard` |

## Мутирующие HTML-эндпоинты (🔒 + POST)

```
/vocabulary/add-to-review/                     {word_id, mark_learned?}  form|JSON
/vocabulary/word/<pk>/notes/                   {notes}
/vocabulary/lists/create/                      {name}
/vocabulary/lists/<pk>/add/<word_id>/          —
/vocabulary/lists/<pk>/remove/<word_id>/       —
/vocabulary/lists/<pk>/export/                 → CSV (GET, но личный)
/quiz/<pk>/submit/                             q_<id>=<answer_id|text>…
/library/{korean|japanese}/api/word-lookup/?word=        GET JSON
/library/{korean|japanese}/api/add-to-vocab/             POST {word_id}
/library/{korean|japanese}/api/highlight/toggle|update|delete/   POST
/library/{korean|japanese}/api/bookmark/update|delete/           POST
/library/<slug>/ (POST)                        action=toggle_read|toggle_bookmark|
                                               save_note|delete_note|add_tag|remove_tag
```

Внимание: у `library` есть легаси-дубль без языкового префикса (`/library/search/`
и т.п. → ko) и catch-all `/library/<slug>/` → redirect на ko-detail.
