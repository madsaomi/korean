# Справочник моделей

Быстрая шпаргалка по моделям и связям. Поля перечислены не все — только важные
для логики. Полные определения в `*/models.py`.

## accounts
- `UserProfile` 1:1 User (`related_name='profile'`) — native_language, level (5 choices), avatar
- `Streak` 1:1 User (`streak`) — current_streak, longest_streak, last_active_date (DateField)
- `Achievement` FK User (`achievements`) — code; unique(user, code); `ALL_CODES` = set из 11 кодов
- `DailyGoal` 1:1 User (`daily_goal`) — words/lessons/quizzes_target
- Signal post_save(User) создаёт Profile + Streak + DailyGoal автоматически.

## vocabulary
- `Category` — slug unique, ordering [order]
- `Word` FK Category (`words`) — korean, russian, romanization, level (beginner/elementary/intermediate),
  created_at; **Meta.ordering=['korean']**
- `WordList` FK User (`word_lists`) — M2M words

## progress
- `UserLessonProgress` unique(user, lesson) — completed, score, completed_at
- `UserWordProgress` unique(user, word) — learned, review_count, next_review, notes, learned_at;
  индекс (user, learned, next_review). **Писать только через review/services.py::apply_review**
- `UserQuizResult` — score, total, auto_now_add; Meta.ordering=['-completed_at']; .percentage()

## lessons / grammar / quiz
- `Course` → `Lesson` (`lessons`) → `LessonStep` (`steps`: text/image/quiz)
- `GrammarTopic` (slug unique) → `GrammarRule` (`rules`, examples = JSONField-списки)
  → `GrammarExercise` (option_a..d, correct_answer, difficulty)
- `Quiz` → `Question` (question_type: multiple_choice/true_false/writing)
  → `Answer` (is_correct, explanation). Quiz.time_limit сек (0 = без лимита), passing_score %.

## library (все пользовательские скоупятся по user+language+slug)
- `ReadingProgress` unique(user, language, slug) — read, read_at
- `Bookmark` UniqueConstraint(user, language, slug) — title, anchor, note, color, section
- `Highlight` UniqueConstraint(user, language, slug, text, start_offset, end_offset)
- `Note` — content required, заметок много на slug
- `LibraryTag` unique(user, language, slug, tag)

## Правила работы с моделями
- Меняешь модель → `makemigrations` + проверь `makemigrations --check`.
- related_name'ы фиксированы — не переименовывать (завязаны шаблоны и annotate:
  `lesson_progress`, `quiz_results`, `word_progress`, `word_lists`, `library_*`).
