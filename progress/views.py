from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from progress.models import UserQuizResult, UserLessonProgress, UserWordProgress
from accounts.models import Streak

@login_required
def progress_dashboard(request):
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)

    quizzes = UserQuizResult.objects.filter(user=request.user, completed_at__gte=thirty_days_ago)
    quiz_dates = quizzes.annotate(day=TruncDate('completed_at')).values('day').annotate(count=Count('id')).order_by('day')

    lesson_progress = UserLessonProgress.objects.filter(user=request.user, completed=True).count()
    words_learned = UserWordProgress.objects.filter(user=request.user, learned=True).count()
    total_quizzes = UserQuizResult.objects.filter(user=request.user).count()
    words_in_review = UserWordProgress.objects.filter(user=request.user, learned=False).exclude(next_review=None).count()

    streak = getattr(request.user, 'streak', None)
    if not streak:
        streak = Streak.objects.create(user=request.user)
    today = now.date()
    last_30 = [today - timedelta(days=i) for i in range(29, -1, -1)]
    streak_days = []
    for d in last_30:
        prog = UserLessonProgress.objects.filter(user=request.user, completed_at__date=d).count()
        quiz = UserQuizResult.objects.filter(user=request.user, completed_at__date=d).count()
        streak_days.append({'date': d.isoformat(), 'active': prog > 0 or quiz > 0, 'lessons': prog, 'quizzes': quiz})

    all_results = UserQuizResult.objects.filter(user=request.user)[:20]
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
