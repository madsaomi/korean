from datetime import timedelta

from django.contrib import messages
from django.shortcuts import render
from django.http import Http404
from django.core.exceptions import PermissionDenied
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
                    messages.success(request, f'\U0001f525\U0001f525\U0001f525 {streak.current_streak} дней подряд! Не останавливайся!')
                elif streak.current_streak > was_streak and streak.current_streak > 1:
                    messages.success(request, f'\U0001f525 Уже {streak.current_streak} дней подряд! Молодец!')

            from accounts.models import Achievement
            earned = set(request.user.achievements.values_list('code', flat=True))
            new_achievements = []

            if streak.current_streak >= 3 and 'streak_3' not in earned:
                new_achievements.append(('streak_3', '\U0001f525 3 дня подряд', 'Три дня занятий без перерыва!', '\U0001f525'))
            if streak.current_streak >= 7 and 'streak_7' not in earned:
                new_achievements.append(('streak_7', '\U0001f525\U0001f525 Неделя без пропусков', 'Целая неделя ежедневных занятий!', '\U0001f525'))
            if streak.current_streak >= 30 and 'streak_30' not in earned:
                new_achievements.append(('streak_30', '\U0001f525\U0001f525\U0001f525 Месяц силы', '30 дней подряд — ты легенда!', '\U0001f4aa'))

            from progress.models import UserLessonProgress, UserQuizResult, UserWordProgress
            if 'first_lesson' not in earned or 'five_lessons' not in earned or 'ten_lessons' not in earned:
                lessons_done = UserLessonProgress.objects.filter(user=request.user, completed=True).count()
                if lessons_done >= 1 and 'first_lesson' not in earned:
                    new_achievements.append(('first_lesson', '\U0001f4da Первый урок', 'Пройди свой первый урок', '\U0001f4da'))
                if lessons_done >= 5 and 'five_lessons' not in earned:
                    new_achievements.append(('five_lessons', '\U0001f4da 5 уроков', 'Пройди 5 уроков', '\U0001f4da'))
                if lessons_done >= 10 and 'ten_lessons' not in earned:
                    new_achievements.append(('ten_lessons', '\U0001f4da 10 уроков', 'Пройди 10 уроков — серьёзный подход!', '\U0001f4da'))

            if 'first_quiz' not in earned or 'five_quizzes' not in earned:
                quizzes_done = UserQuizResult.objects.filter(user=request.user).count()
                if quizzes_done >= 1 and 'first_quiz' not in earned:
                    new_achievements.append(('first_quiz', '\U0001f3af Первый тест', 'Пройди свой первый тест', '\U0001f3af'))
                if quizzes_done >= 5 and 'five_quizzes' not in earned:
                    new_achievements.append(('five_quizzes', '\U0001f3af 5 тестов', 'Пройди 5 тестов', '\U0001f3af'))

            if 'ten_words' not in earned or 'fifty_words' not in earned or 'hundred_words' not in earned:
                words_learned = UserWordProgress.objects.filter(user=request.user, learned=True).count()
                if words_learned >= 10 and 'ten_words' not in earned:
                    new_achievements.append(('ten_words', '\U0001f4d6 10 слов', 'Выучи 10 слов', '\U0001f4d6'))
                if words_learned >= 50 and 'fifty_words' not in earned:
                    new_achievements.append(('fifty_words', '\U0001f4d6 50 слов', 'Выучи 50 слов', '\U0001f4d6'))
                if words_learned >= 100 and 'hundred_words' not in earned:
                    new_achievements.append(('hundred_words', '\U0001f4d6\U0001f4af 100 слов', 'Выучи 100 слов — отлично!', '\U0001f4af'))

            for code, title, desc, icon in new_achievements:
                achievement, created = Achievement.objects.get_or_create(
                    user=request.user, code=code,
                    defaults={'title': title, 'description': desc, 'icon': icon}
                )
                if created:
                    messages.success(request, f'{icon} Достижение разблокировано: {title}!', extra_tags='achievement-unlock')

        return self.get_response(request)


class ErrorPageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code in (404, 403, 400):
            tmpl = f'{response.status_code}.html'
            return render(request, tmpl, status=response.status_code)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, Http404):
            return render(request, '404.html', status=404)
        if isinstance(exception, PermissionDenied):
            return render(request, '403.html', status=403)
        return render(request, '500.html', status=500)
