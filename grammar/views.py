import random
from django.shortcuts import render, get_object_or_404, redirect
from .models import GrammarTopic, GrammarExercise

def grammar_list(request):
    from django.db.models import Count
    topics = GrammarTopic.objects.annotate(rule_count=Count('rules'))
    return render(request, 'grammar/list.html', {'topics': topics})

def grammar_detail(request, slug):
    topic = get_object_or_404(GrammarTopic, slug=slug)
    rules = topic.rules.all()
    for rule in rules:
        rule.paired_examples = zip(
            rule.korean_examples or [],
            rule.russian_examples or []
        )
    return render(request, 'grammar/detail.html', {'topic': topic, 'rules': rules})

def exercise_list(request):
    difficulties = GrammarExercise.DIFFICULTY
    topic_filter = request.GET.get('topic', '')
    difficulty_filter = request.GET.get('difficulty', '')

    exercises = GrammarExercise.objects.all()
    if topic_filter:
        exercises = exercises.filter(topic__slug=topic_filter)
    if difficulty_filter:
        exercises = exercises.filter(difficulty=difficulty_filter)

    count = exercises.count()
    topics = GrammarTopic.objects.all()
    return render(request, 'grammar/exercise_list.html', {
        'exercises': exercises,
        'topics': topics,
        'difficulties': difficulties,
        'topic_filter': topic_filter,
        'difficulty_filter': difficulty_filter,
        'count': count,
    })

def start_exercise(request):
    topic = request.GET.get('topic', '')
    difficulty = request.GET.get('difficulty', '')
    count = request.GET.get('count', '10')

    try:
        count = max(1, min(50, int(count)))
    except (ValueError, TypeError):
        count = 10

    exercises = GrammarExercise.objects.all()
    if topic:
        exercises = exercises.filter(topic__slug=topic)
    if difficulty:
        exercises = exercises.filter(difficulty=difficulty)

    exercises = list(exercises)
    random.shuffle(exercises)
    exercises = exercises[:min(count, len(exercises))]

    request.session['grammar_exercise_ids'] = [e.id for e in exercises]
    request.session['grammar_exercise_index'] = 0
    request.session['grammar_exercise_correct'] = 0
    request.session['grammar_exercise_total'] = len(exercises)

    return redirect('grammar:do_exercise')

def do_exercise(request):
    exercise_ids = request.session.get('grammar_exercise_ids', [])
    index = request.session.get('grammar_exercise_index', 0)

    if not exercise_ids or index >= len(exercise_ids):
        return redirect('grammar:exercise_result')

    exercise = get_object_or_404(GrammarExercise, id=exercise_ids[index])
    total = len(exercise_ids)

    if request.method == 'POST':
        selected = request.POST.get('answer', '')
        if selected == exercise.correct_answer:
            request.session['grammar_exercise_correct'] = request.session.get('grammar_exercise_correct', 0) + 1
            request.session['grammar_exercise_last_result'] = True
        else:
            request.session['grammar_exercise_last_result'] = False
        request.session['grammar_exercise_last_answer'] = selected
        request.session['grammar_exercise_last_correct'] = exercise.correct_answer
        request.session['grammar_exercise_last_explanation'] = exercise.explanation
        request.session['grammar_exercise_index'] = index + 1

        if index + 1 >= total:
            return redirect('grammar:exercise_result')
        return redirect('grammar:do_exercise')

    last_result = request.session.pop('grammar_exercise_last_result', None)
    last_answer = request.session.pop('grammar_exercise_last_answer', None)
    last_correct = request.session.pop('grammar_exercise_last_correct', None)
    last_explanation = request.session.pop('grammar_exercise_last_explanation', None)

    return render(request, 'grammar/exercise_do.html', {
        'exercise': exercise,
        'index': index + 1,
        'total': total,
        'progress_pct': int((index / total) * 100) if total else 0,
        'last_result': last_result,
        'last_answer': last_answer,
        'last_correct': last_correct,
        'last_explanation': last_explanation,
    })

def exercise_result(request):
    correct = request.session.get('grammar_exercise_correct', 0)
    total = request.session.get('grammar_exercise_total', 0)
    return render(request, 'grammar/exercise_result.html', {
        'correct': correct,
        'total': total,
        'percentage': round(correct / total * 100) if total else 0,
    })
