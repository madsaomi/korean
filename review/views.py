import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from progress.models import UserWordProgress
from review.services import InvalidReviewAction, apply_review, pending_review_count
from vocabulary.models import Word


def _parse_review_payload(request):
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return None, None
    else:
        data = request.POST
    return data.get('word_id'), data.get('action')


@login_required
def review_page(request):
    session_key = 'review_session'

    # Handle session reset early, before any DB work
    if request.GET.get('reset_session'):
        request.session.pop(session_key, None)
        return redirect('review')

    now = timezone.now()

    if session_key not in request.session:
        request.session[session_key] = {'start': now.isoformat(), 'completed': 0, 'again': 0, 'good': 0, 'easy': 0}

    session = request.session[session_key]

    due_words = UserWordProgress.objects.filter(
        user=request.user, next_review__lte=now
    ).select_related('word__category')[:20]

    if request.method == 'POST':
        word_id, action = _parse_review_payload(request)
        is_ajax = (
            request.headers.get('x-requested-with') == 'XMLHttpRequest' or
            request.content_type == 'application/json'
        )
        if not word_id or not action:
            return JsonResponse({'success': False, 'error': 'missing fields'}, status=400) \
                if is_ajax else HttpResponseBadRequest('Missing fields')

        try:
            prog = apply_review(request.user, word_id, action)
        except (InvalidReviewAction, ValueError, TypeError):
            return JsonResponse({'success': False, 'error': 'invalid action'}, status=400) \
                if is_ajax else HttpResponseBadRequest('Invalid action')

        if prog is None:
            return JsonResponse({'success': False, 'error': 'word_not_found'}, status=404) \
                if is_ajax else redirect('review')

        session['completed'] += 1
        session[action] = session.get(action, 0) + 1
        request.session.modified = True

        if is_ajax:
            return JsonResponse({
                'success': True,
                'action': action,
                'learned': prog.learned,
                'next_review': prog.next_review.isoformat(),
                'pending_count': pending_review_count(request.user),
            })
        return redirect('review')

    recent_words = Word.objects.filter(
        word_lists__user=request.user
    ).order_by('-created_at').distinct()[:5]

    ctx = {
        'due_words': due_words,
        'pending_count': pending_review_count(request.user),
        'recent_words': recent_words,
    }

    if session['completed'] > 0:
        ctx['session_summary'] = session

    return render(request, 'review/index.html', ctx)

@login_required
def flashcard_mode(request):
    now = timezone.now()
    cards = UserWordProgress.objects.filter(
        user=request.user, next_review__lte=now
    ).select_related('word__category')[:50]

    if request.method == 'POST':
        word_id, action = _parse_review_payload(request)
        is_ajax = (
            request.headers.get('x-requested-with') == 'XMLHttpRequest' or
            request.content_type == 'application/json'
        )

        if not word_id or not action:
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'missing fields'}, status=400)
            return HttpResponseBadRequest('Missing fields')

        try:
            prog = apply_review(request.user, word_id, action)
        except (InvalidReviewAction, ValueError, TypeError):
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'invalid action'}, status=400)
            return HttpResponseBadRequest('Invalid action')

        if prog is None and is_ajax:
            return JsonResponse({'success': False, 'error': 'word_not_found'}, status=404)

        if is_ajax:
            return JsonResponse({
                'success': True,
                'action': action,
                'learned': prog.learned,
                'next_review': prog.next_review.isoformat(),
            })
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
