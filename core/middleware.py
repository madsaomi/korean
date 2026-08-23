import logging
from datetime import timedelta

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import render
from django.utils import timezone

from accounts.models import Streak
from accounts.utils import (
    check_lesson_achievements,
    check_quiz_achievements,
    check_word_achievements,
    grant_achievement,
)

logger = logging.getLogger(__name__)


class StreakMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Cache streak check in session — only hit DB once per day
            session = getattr(request, 'session', None)
            if session is None:
                return self.get_response(request)

            today_str = timezone.localdate().isoformat()
            if session.get('streak_checked_date') == today_str:
                return self.get_response(request)

            streak, _ = Streak.objects.get_or_create(user=request.user)

            today = timezone.localdate()
            last = streak.last_active_date
            if last is None or last != today:
                was_streak = streak.current_streak
                if last == today - timedelta(days=1):
                    streak.current_streak += 1
                elif last is None or last < today - timedelta(days=1):
                    streak.current_streak = 1
                streak.longest_streak = max(streak.longest_streak, streak.current_streak)
                streak.last_active_date = today
                streak.save(update_fields=['current_streak', 'longest_streak', 'last_active_date'])
                if streak.current_streak > was_streak and streak.current_streak > 1 and streak.current_streak % 7 == 0:
                    messages.success(request, f'\U0001f525\U0001f525\U0001f525 {streak.current_streak} дней подряд! Не останавливайся!')
                elif streak.current_streak > was_streak and streak.current_streak > 1:
                    messages.success(request, f'\U0001f525 Уже {streak.current_streak} дней подряд! Молодец!')

                # --- Achievement checks: streak-based (run once per day) ---
                if streak.current_streak >= 3:
                    grant_achievement(request.user, 'streak_3', request)
                if streak.current_streak >= 7:
                    grant_achievement(request.user, 'streak_7', request)
                if streak.current_streak >= 30:
                    grant_achievement(request.user, 'streak_30', request)

                # Other achievement checks (lessons, quizzes, words) — delegated to utils
                check_lesson_achievements(request.user, request)
                check_quiz_achievements(request.user, request)
                check_word_achievements(request.user, request)

            session['streak_checked_date'] = today_str

        return self.get_response(request)


class ErrorPageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        # 4xx (Http404, PermissionDenied, SuspiciousOperation, etc.) are
        # rendered by handler400/403/404 defined in config/urls.py.
        # Only unhandled server errors are handled here.
        if getattr(request, '_error_handled', False):
            return None
        if isinstance(exception, (Http404, PermissionDenied)):
            return None
        request._error_handled = True
        logger.exception('Unhandled exception')
        try:
            return render(request, '500.html', status=500)
        except Exception:
            logger.exception('Error rendering error page')
            return None
