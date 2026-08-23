from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.utils import check_lesson_achievements, check_quiz_achievements
from progress.models import UserLessonProgress, UserQuizResult

from .models import Quiz

TIMER_GRACE_SECONDS = 60
SESSION_START_PREFIX = 'quiz_started_'
RESUBMIT_COOLDOWN_SECONDS = 30


def _normalize_text(value):
    return ' '.join(value.split()).lower()


def quiz_list(request):
    quizzes = Quiz.objects.annotate(q_count=Count('questions'))
    return render(request, 'quiz/list.html', {'quizzes': quizzes})


def quiz_detail(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    questions = quiz.questions.prefetch_related('answers')
    if quiz.time_limit > 0:
        request.session[SESSION_START_PREFIX + str(pk)] = timezone.now().isoformat()
    return render(request, 'quiz/detail.html', {
        'quiz': quiz,
        'questions': questions,
        'timer': quiz.time_limit,
        'timer_min': quiz.time_limit // 60,
        'timer_sec': quiz.time_limit % 60,
    })


def _time_limit_exceeded(request, quiz):
    """Server-side timer check: the attempt must start with a detail-page visit."""
    if quiz.time_limit <= 0:
        return False
    started_raw = request.session.get(SESSION_START_PREFIX + str(quiz.pk))
    if not started_raw:
        return True
    try:
        started = datetime.fromisoformat(started_raw)
    except (TypeError, ValueError):
        return True
    if timezone.is_naive(started):
        started = timezone.make_aware(started, timezone.get_default_timezone())
    elapsed = (timezone.now() - started).total_seconds()
    return elapsed > quiz.time_limit + TIMER_GRACE_SECONDS


@login_required
@require_POST
@transaction.atomic
def quiz_submit(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    questions = list(quiz.questions.prefetch_related('answers'))
    total = len(questions)

    start_key = SESSION_START_PREFIX + str(pk)
    exceeded = _time_limit_exceeded(request, quiz)
    request.session.pop(start_key, None)

    last_attempt = (
        UserQuizResult.objects.filter(user=request.user, quiz=quiz)
        .order_by('-completed_at').first()
    )
    if last_attempt and (timezone.now() - last_attempt.completed_at).total_seconds() < RESUBMIT_COOLDOWN_SECONDS:
        messages.warning(request, '⏳ Слишком часто — подожди немного перед следующей попыткой.')
        return redirect('quiz_detail', pk=pk)

    if exceeded:
        messages.warning(request, '⏰ Время вышло — попытка не засчитана. Пройдите тест заново.')
        return redirect('quiz_detail', pk=pk)

    score = 0
    results = []

    for q in questions:
        raw = request.POST.get(f'q_{q.id}', '').strip()
        answers = list(q.answers.all())
        correct_ids = {str(a.id) for a in answers if a.is_correct}
        correct_texts = {_normalize_text(a.text) for a in answers if a.is_correct}
        correct_answer = next((a for a in answers if a.is_correct), None)

        # Radio inputs submit the answer id; writing questions submit free text.
        if q.question_type == 'writing':
            selected_text = raw
            is_correct = _normalize_text(raw) in correct_texts
        elif raw.isdigit():
            selected_answer = next((a for a in answers if str(a.id) == raw), None)
            selected_text = selected_answer.text if selected_answer else ''
            is_correct = bool(selected_answer and str(selected_answer.id) in correct_ids)
        else:
            selected_text = raw
            is_correct = _normalize_text(raw) in correct_texts

        if is_correct:
            score += 1
        results.append({
            'question': q,
            'selected': selected_text,
            'correct_answer': correct_answer.text if correct_answer else '',
            'is_correct': is_correct,
            'explanation': correct_answer.explanation if correct_answer else '',
        })

    UserQuizResult.objects.create(
        user=request.user,
        quiz=quiz,
        score=score,
        total=total,
    )

    percentage = int((score / total) * 100) if total else 0

    if percentage >= quiz.passing_score and quiz.lesson:
        UserLessonProgress.objects.update_or_create(
            user=request.user, lesson=quiz.lesson,
            defaults={'completed': True, 'score': percentage, 'completed_at': timezone.now()}
        )

    check_lesson_achievements(request.user, request)
    check_quiz_achievements(request.user, request)

    return render(request, 'quiz/result.html', {
        'quiz': quiz,
        'score': score,
        'wrong': total - score,
        'total': total,
        'percentage': percentage,
        'results': results,
        'passed': percentage >= quiz.passing_score,
    })
