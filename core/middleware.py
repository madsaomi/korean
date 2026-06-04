from datetime import timedelta
from django.contrib import messages
from django.utils import timezone
from accounts.models import Streak

class StreakMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            streak = Streak.objects.filter(user=request.user).first()
            if not streak:
                streak = Streak.objects.create(user=request.user)
            today = timezone.now().date()
            last = streak.last_active_date
            if last != today:
                was_streak = streak.current_streak
                if last == today - timedelta(days=1):
                    streak.current_streak += 1
                elif last < today - timedelta(days=1):
                    streak.current_streak = 1
                if streak.current_streak > streak.longest_streak:
                    streak.longest_streak = streak.current_streak
                streak.last_active_date = today
                streak.save(update_fields=['current_streak', 'longest_streak', 'last_active_date'])
                if streak.current_streak > was_streak and streak.current_streak > 1 and streak.current_streak % 7 == 0:
                    messages.success(request, f'🔥🔥🔥 {streak.current_streak} дней подряд! Не останавливайся!')
                elif streak.current_streak > was_streak and streak.current_streak > 1:
                    messages.success(request, f'🔥 Уже {streak.current_streak} дней подряд! Молодец!')

            from accounts.models import Achievement
            earned = set(request.user.achievements.values_list('code', flat=True))
            new_achievements = []

            if streak.current_streak >= 3 and 'streak_3' not in earned:
                new_achievements.append(('streak_3', '🔥 3 дня подряд', 'Три дня занятий без перерыва!', '🔥'))
            if streak.current_streak >= 7 and 'streak_7' not in earned:
                new_achievements.append(('streak_7', '🔥🔥 Неделя без пропусков', 'Целая неделя ежедневных занятий!', '🔥'))
            if streak.current_streak >= 30 and 'streak_30' not in earned:
                new_achievements.append(('streak_30', '🔥🔥🔥 Месяц силы', '30 дней подряд — ты легенда!', '💪'))

            from progress.models import UserLessonProgress, UserQuizResult, UserWordProgress
            if 'first_lesson' not in earned or 'five_lessons' not in earned or 'ten_lessons' not in earned:
                lessons_done = UserLessonProgress.objects.filter(user=request.user, completed=True).count()
                if lessons_done >= 1 and 'first_lesson' not in earned:
                    new_achievements.append(('first_lesson', '📚 Первый урок', 'Пройди свой первый урок', '📚'))
                if lessons_done >= 5 and 'five_lessons' not in earned:
                    new_achievements.append(('five_lessons', '📚 5 уроков', 'Пройди 5 уроков', '📚'))
                if lessons_done >= 10 and 'ten_lessons' not in earned:
                    new_achievements.append(('ten_lessons', '📚 10 уроков', 'Пройди 10 уроков — серьёзный подход!', '📚'))

            if 'first_quiz' not in earned or 'five_quizzes' not in earned:
                quizzes_done = UserQuizResult.objects.filter(user=request.user).count()
                if quizzes_done >= 1 and 'first_quiz' not in earned:
                    new_achievements.append(('first_quiz', '🎯 Первый тест', 'Пройди свой первый тест', '🎯'))
                if quizzes_done >= 5 and 'five_quizzes' not in earned:
                    new_achievements.append(('five_quizzes', '🎯 5 тестов', 'Пройди 5 тестов', '🎯'))

            if 'ten_words' not in earned or 'fifty_words' not in earned or 'hundred_words' not in earned:
                words_learned = UserWordProgress.objects.filter(user=request.user, learned=True).count()
                if words_learned >= 10 and 'ten_words' not in earned:
                    new_achievements.append(('ten_words', '📖 10 слов', 'Выучи 10 слов', '📖'))
                if words_learned >= 50 and 'fifty_words' not in earned:
                    new_achievements.append(('fifty_words', '📖 50 слов', 'Выучи 50 слов', '📖'))
                if words_learned >= 100 and 'hundred_words' not in earned:
                    new_achievements.append(('hundred_words', '📖💯 100 слов', 'Выучи 100 слов — отлично!', '💯'))

            for code, title, desc, icon in new_achievements:
                achievement, created = Achievement.objects.get_or_create(
                    user=request.user, code=code,
                    defaults={'title': title, 'description': desc, 'icon': icon}
                )
                if created:
                    messages.success(request, f'{icon} Достижение разблокировано: {title}!', extra_tags='achievement-unlock')

        return self.get_response(request)
