import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from vocabulary.models import Word
from progress.models import UserWordProgress
from accounts.utils import check_word_achievements

@login_required
def review_page(request):
    now = timezone.now()

    session_key = 'review_session'
    if session_key not in request.session:
        request.session[session_key] = {'start': now.isoformat(), 'completed': 0, 'again': 0, 'good': 0, 'easy': 0}

    session = request.session[session_key]

    due_words = UserWordProgress.objects.filter(
        user=request.user, next_review__lte=now, learned=False
    ).select_related('word')[:20]

    if request.method == 'POST':
        word_id = None
        action = None
        is_ajax = (                request.headers.get('x-requested-with') == 'XMLHttpRequest' or 
                   request.content_type == 'application/json')
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                word_id = data.get('word_id')
                action = data.get('action')
            except json.JSONDecodeError:
                pass
        else:
            word_id = request.POST.get('word_id')
            action = request.POST.get('action')

        if word_id and action:
            prog = UserWordProgress.objects.filter(
                user=request.user, word_id=word_id
            ).first()
            if prog:
                prog.review_count += 1
                if action == 'easy':
                    prog.next_review = now + timezone.timedelta(days=7)
                    prog.learned = True
                    if not prog.learned_at:
                        prog.learned_at = now
                    check_word_achievements(request.user, request)
                elif action == 'good':
                    base_days = [1, 3, 7, 14, 30]
                    days = base_days[min(prog.review_count - 1, len(base_days) - 1)]
                    prog.next_review = now + timezone.timedelta(days=days)
                elif action == 'again':
                    prog.next_review = now + timezone.timedelta(hours=1)
                prog.save(update_fields=['review_count', 'next_review', 'learned', 'learned_at'])
                session['completed'] += 1
                session[action] = session.get(action, 0) + 1
                request.session.modified = True
        return redirect('review')

    pending_count = UserWordProgress.objects.filter(
        user=request.user, next_review__lte=now, learned=False
    ).count()

    recent_words = Word.objects.filter(
        word_lists__user=request.user
    ).distinct()[:5]

    ctx = {
        'due_words': due_words,
        'pending_count': pending_count,
        'recent_words': recent_words,
    }

    if session['completed'] > 0:
        ctx['session_summary'] = session

    if request.GET.get('reset_session'):
        request.session.pop(session_key, None)
        return redirect('review')

    return render(request, 'review/index.html', ctx)

@login_required
def flashcard_mode(request):
    now = timezone.now()
    cards = UserWordProgress.objects.filter(
        user=request.user, next_review__lte=now, learned=False
    ).select_related('word')[:50]

    if request.method == 'POST':
        word_id = None
        action = None
        is_ajax = (request.headers.get('x-requested-with') == 'XMLHttpRequest' or 
                   request.content_type == 'application/json')
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                word_id = data.get('word_id')
                action = data.get('action')
            except json.JSONDecodeError:
                pass
        else:
            word_id = request.POST.get('word_id')
            action = request.POST.get('action')

        if word_id and action:
            prog = UserWordProgress.objects.filter(
                user=request.user, word_id=word_id
            ).first()
            if prog:
                prog.review_count += 1
                if action == 'easy':
                    prog.next_review = now + timezone.timedelta(days=7)
                    prog.learned = True
                    if not prog.learned_at:
                        prog.learned_at = now
                    check_word_achievements(request.user, request)
                elif action == 'good':
                    base_days = [1, 3, 7, 14, 30]
                    days = base_days[min(prog.review_count - 1, len(base_days) - 1)]
                    prog.next_review = now + timezone.timedelta(days=days)
                elif action == 'again':
                    prog.next_review = now + timezone.timedelta(hours=1)
                prog.save(update_fields=['review_count', 'next_review', 'learned', 'learned_at'])
        if is_ajax:
            from django.http import JsonResponse
            return JsonResponse({'success': True})
        return redirect('flashcard')

    cards_data = [
        {
            'id': p.word.id,
            'korean': p.word.korean,
            'russian': p.word.russian,
            'romanization': p.word.romanization,
            'example': p.word.example_sentence,
            'example_tr': p.word.example_translation,
            'category': p.word.category.name,
        }
        for p in cards
    ]

    return render(request, 'review/flashcard.html', {
        'cards_json': json.dumps(cards_data),
        'card_count': len(cards_data),
    })
