from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.encoding import force_str

from accounts.models import DailyGoal, Streak
from progress.models import UserLessonProgress, UserQuizResult, UserWordProgress


@login_required
def progress_dashboard(request):
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)

    lesson_progress = UserLessonProgress.objects.filter(user=request.user, completed=True).count()
    words_learned = UserWordProgress.objects.filter(user=request.user, learned=True).count()
    total_quizzes = UserQuizResult.objects.filter(user=request.user).count()
    words_in_review = UserWordProgress.objects.filter(
        user=request.user, next_review__lte=now
    ).count()

    streak, _ = Streak.objects.get_or_create(user=request.user)
    today = timezone.localdate()
    last_30 = [today - timedelta(days=i) for i in range(29, -1, -1)]

    lesson_agg = (
        UserLessonProgress.objects
        .filter(user=request.user, completed_at__gte=thirty_days_ago)
        .annotate(day=TruncDate('completed_at'))
        .values('day').annotate(count=Count('id'))
    )
    quiz_agg = (
        UserQuizResult.objects
        .filter(user=request.user, completed_at__gte=thirty_days_ago)
        .annotate(day=TruncDate('completed_at'))
        .values('day').annotate(count=Count('id'))
    )
    lesson_by_day = {row['day']: row['count'] for row in lesson_agg}
    quiz_by_day = {row['day']: row['count'] for row in quiz_agg}

    streak_days = []
    for d in last_30:
        prog = lesson_by_day.get(d, 0)
        quiz = quiz_by_day.get(d, 0)
        streak_days.append({'date': d.isoformat(), 'active': prog > 0 or quiz > 0, 'lessons': prog, 'quizzes': quiz})

    all_results = UserQuizResult.objects.filter(user=request.user).select_related('quiz')[:20]
    quiz_scores = [{'title': r.quiz.title, 'score': r.percentage(), 'total': r.total, 'date': r.completed_at.isoformat()} for r in all_results]

    return render(request, 'progress/dashboard.html', {
        'lesson_progress': lesson_progress,
        'words_learned': words_learned,
        'total_quizzes': total_quizzes,
        'words_in_review': words_in_review,
        'streak_days': streak_days,
        'quiz_scores': quiz_scores,
        'streak': streak,
    })


@login_required
def progress_export(request):
    """Full personal-progress dump as a downloadable JSON file."""
    user = request.user
    streak, _ = Streak.objects.get_or_create(user=user)
    goal, _ = DailyGoal.objects.get_or_create(user=user)

    words = UserWordProgress.objects.filter(user=user).select_related('word__category')
    lessons = UserLessonProgress.objects.filter(user=user).select_related('lesson')
    quizzes = UserQuizResult.objects.filter(user=user).select_related('quiz')

    payload = {
        'exported_at': timezone.now().isoformat(),
        'user': {
            'username': user.username,
            'level': user.profile.level,
            'native_language': user.profile.native_language,
            'streak': {
                'current': streak.current_streak,
                'longest': streak.longest_streak,
                'last_active_date': force_str(streak.last_active_date or ''),
                'freezes': streak.freezes,
            },
            'daily_goal': {
                'words': goal.words_target,
                'lessons': goal.lessons_target,
                'quizzes': goal.quizzes_target,
            },
        },
        'achievements': list(user.achievements.values('code', 'title', 'earned_at')),
        'words': [
            {
                'korean': p.word.korean,
                'russian': p.word.russian,
                'category': p.word.category.name if p.word.category else '',
                'level': p.word.level,
                'learned': p.learned,
                'review_count': p.review_count,
                'next_review': p.next_review.isoformat(),
                'learned_at': p.learned_at.isoformat() if p.learned_at else None,
                'notes': p.notes,
            }
            for p in words
        ],
        'lessons': [
            {
                'course': l.lesson.course.title,
                'lesson': l.lesson.title,
                'completed': l.completed,
                'score': l.score,
                'completed_at': l.completed_at.isoformat() if l.completed_at else None,
            }
            for l in lessons
        ],
        'quizzes': [
            {
                'quiz': q.quiz.title,
                'score': q.score,
                'total': q.total,
                'percentage': q.percentage(),
                'completed_at': q.completed_at.isoformat(),
            }
            for q in quizzes
        ],
    }

    response = JsonResponse(payload, json_dumps_params={'ensure_ascii': False, 'indent': 2})
    response['Content-Disposition'] = f'attachment; filename="klab-progress-{timezone.localdate()}.json"'
    return response
