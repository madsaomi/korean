from django.contrib import messages
from accounts.models import Achievement
from progress.models import UserLessonProgress, UserQuizResult, UserWordProgress


def grant_achievement(user, code, title, description, icon, request=None):
    achievement, created = Achievement.objects.get_or_create(
        user=user, code=code,
        defaults={'title': title, 'description': description, 'icon': icon}
    )
    if created and request:
        messages.success(
            request,
            f'{icon} Достижение разблокировано: {title}!',
            extra_tags='achievement-unlock'
        )
    return created


def check_lesson_achievements(user, request=None):
    lessons_done = UserLessonProgress.objects.filter(
        user=user, completed=True
    ).count()

    if lessons_done >= 1:
        grant_achievement(user, 'first_lesson', '📚 Первый урок',
                          'Пройди свой первый урок', '📚', request)
    if lessons_done >= 5:
        grant_achievement(user, 'five_lessons', '📚 5 уроков',
                          'Пройди 5 уроков', '📚', request)
    if lessons_done >= 10:
        grant_achievement(user, 'ten_lessons', '📚 10 уроков',
                          'Пройди 10 уроков — серьёзный подход!', '📚', request)


def check_quiz_achievements(user, request=None):
    quizzes_done = UserQuizResult.objects.filter(user=user).count()

    if quizzes_done >= 1:
        grant_achievement(user, 'first_quiz', '🎯 Первый тест',
                          'Пройди свой первый тест', '🎯', request)
    if quizzes_done >= 5:
        grant_achievement(user, 'five_quizzes', '🎯 5 тестов',
                          'Пройди 5 тестов', '🎯', request)


def check_word_achievements(user, request=None):
    words_learned = UserWordProgress.objects.filter(
        user=user, learned=True
    ).count()

    if words_learned >= 10:
        grant_achievement(user, 'ten_words', '📖 10 слов',
                          'Выучи 10 слов', '📖', request)
    if words_learned >= 50:
        grant_achievement(user, 'fifty_words', '📖 50 слов',
                          'Выучи 50 слов', '📖', request)
    if words_learned >= 100:
        grant_achievement(user, 'hundred_words', '📖💯 100 слов',
                          'Выучи 100 слов — отлично!', '💯', request)
