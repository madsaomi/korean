from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import Count
from django.utils import timezone
from .models import Quiz, Question, Answer
from progress.models import UserLessonProgress, UserQuizResult
from accounts.utils import check_lesson_achievements, check_quiz_achievements

def quiz_list(request):
    quizzes = Quiz.objects.annotate(q_count=Count('questions'))
    return render(request, 'quiz/list.html', {'quizzes': quizzes})

def quiz_detail(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    questions = quiz.questions.all()
    return render(request, 'quiz/detail.html', {
        'quiz': quiz,
        'questions': questions,
        'timer': quiz.time_limit,
        'timer_min': quiz.time_limit // 60,
        'timer_sec': quiz.time_limit % 60,
    })

@login_required
@require_POST
def quiz_submit(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    questions = quiz.questions.all()
    score = 0
    total = questions.count()
    results = []

    for q in questions:
        selected = request.POST.get(f'q_{q.id}')
        correct_answers = q.answers.filter(is_correct=True)
        correct_texts = [a.text for a in correct_answers]
        is_correct = (selected or '').strip() in [t.strip() for t in correct_texts]
        if is_correct:
            score += 1
        correct_answer = correct_answers.first()
        results.append({
            'question': q,
            'selected': selected,
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

    if percentage >= quiz.passing_score:
        if quiz.lesson:
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
