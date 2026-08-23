from django.contrib import messages

from accounts.models import Achievement
from progress.models import UserLessonProgress, UserQuizResult, UserWordProgress


def grant_achievement(user, code, request=None):
    """Grant an achievement by its code from Achievement.CATALOG.

    Returns True if the achievement was newly created.
    """
    if code not in Achievement.CATALOG:
        return False
    icon, title, description = Achievement.CATALOG[code]
    _, created = Achievement.objects.get_or_create(
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
        grant_achievement(user, 'first_lesson', request)
    if lessons_done >= 5:
        grant_achievement(user, 'five_lessons', request)
    if lessons_done >= 10:
        grant_achievement(user, 'ten_lessons', request)


def check_quiz_achievements(user, request=None):
    quizzes_done = UserQuizResult.objects.filter(user=user).count()

    if quizzes_done >= 1:
        grant_achievement(user, 'first_quiz', request)
    if quizzes_done >= 5:
        grant_achievement(user, 'five_quizzes', request)


def check_word_achievements(user, request=None):
    words_learned = UserWordProgress.objects.filter(
        user=user, learned=True
    ).count()

    if words_learned >= 10:
        grant_achievement(user, 'ten_words', request)
    if words_learned >= 50:
        grant_achievement(user, 'fifty_words', request)
    if words_learned >= 100:
        grant_achievement(user, 'hundred_words', request)
