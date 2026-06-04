import random
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count, OuterRef, Subquery, Q
from django.contrib.auth.models import User
from lessons.models import Course, Lesson
from vocabulary.models import Category, Word
from quiz.models import Quiz
from progress.models import UserLessonProgress, UserWordProgress, UserQuizResult
from accounts.models import Streak
from grammar.models import GrammarTopic

def leaderboard(request):
    top_streak = Streak.objects.select_related('user').order_by('-current_streak')[:10]
    top_lessons = User.objects.annotate(
        cnt=Count('lesson_progress', filter=Q(lesson_progress__completed=True))
    ).order_by('-cnt')[:10]
    top_quizzes = User.objects.annotate(
        cnt=Count('quiz_results')
    ).order_by('-cnt')[:10]
    return render(request, 'leaderboard.html', {
        'top_streak': top_streak,
        'top_lessons': top_lessons,
        'top_quizzes': top_quizzes,
    })

def random_word_api(request):
    word = Word.objects.order_by('?').first()
    if not word:
        return JsonResponse({'error': 'no words'}, status=404)
    return JsonResponse({
        'id': word.id,
        'korean': word.korean,
        'russian': word.russian,
        'romanization': word.romanization,
        'category': word.category.name,
        'category_slug': word.category.slug,
        'example': word.example_sentence,
        'example_tr': word.example_translation,
        'level': word.get_level_display(),
    })

def index(request):
    courses = Course.objects.annotate(lesson_count=Count('lessons'))[:3]
    categories = Category.objects.annotate(word_count=Count('words'))[:6]
    quizzes = Quiz.objects.annotate(q_count=Count('questions'))[:3]
    ctx = {'courses': courses, 'categories': categories, 'quizzes': quizzes}

    word_count = Word.objects.count()
    if word_count:
        random_idx = random.randint(0, word_count - 1)
        word_of_day = Word.objects.order_by('pk')[random_idx]
        ctx['word_of_day'] = word_of_day

    if request.user.is_authenticated:
        streak = getattr(request.user, 'streak', None)
        if not streak:
            streak = Streak.objects.create(user=request.user)
        lessons_done = UserLessonProgress.objects.filter(user=request.user, completed=True).count()
        words_learned = UserWordProgress.objects.filter(user=request.user, learned=True).count()
        quizzes_done = UserQuizResult.objects.filter(user=request.user).count()
        last_quiz = UserQuizResult.objects.filter(user=request.user).first()
        words_in_review = UserWordProgress.objects.filter(
            user=request.user, learned=False
        ).exclude(next_review=None).count()
        total_lessons = Lesson.objects.count()
        ctx.update({
            'streak': streak,
            'lessons_done': lessons_done,
            'words_learned': words_learned,
            'quizzes_done': quizzes_done,
            'last_quiz': last_quiz,
            'words_in_review': words_in_review,
            'total_lessons': total_lessons,
        })

    return render(request, 'index.html', ctx)

def unified_search(request):
    query = request.GET.get('q', '').strip()
    cat = request.GET.get('cat', '')
    level = request.GET.get('level', '')
    words = []
    grammar = []
    lessons = []
    categories = Category.objects.all()
    levels = ['beginner', 'elementary', 'intermediate']
    if query:
        wq = Word.objects.filter(
            Q(korean__icontains=query) | Q(russian__icontains=query) | Q(romanization__icontains=query)
        )
        if cat:
            wq = wq.filter(category__slug=cat)
        if level:
            wq = wq.filter(level=level)
        words = wq.select_related('category')[:20]
        grammar = GrammarTopic.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )[:5]
        lessons = Lesson.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        ).select_related('course')[:5]
    return render(request, 'search.html', {
        'query': query,
        'words': words,
        'grammar': grammar,
        'lessons': lessons,
        'categories': categories,
        'levels': levels,
        'selected_cat': cat,
        'selected_level': level,
    })
