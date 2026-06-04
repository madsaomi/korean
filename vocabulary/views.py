from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Category, Word, WordList
from progress.models import UserWordProgress
import csv
import re
import urllib.parse

def study_custom(request):
    categories = Category.objects.all()
    levels = Word._meta.get_field('level').choices
    cat = request.GET.get('cat', '')
    level = request.GET.get('level', '')
    try:
        count = max(1, min(100, int(request.GET.get('count', 10))))
    except (ValueError, TypeError):
        count = 10

    qs = Word.objects.all()
    if cat:
        qs = qs.filter(category__slug=cat)
    if level:
        qs = qs.filter(level=level)
    words = list(qs.order_by('?')[:count])
    total = len(words)
    if total == 0:
        words = []
        current_word = None
        current = 0
        prev_word = None
        next_word = None
        revealed = False
    else:
        word_id = request.GET.get('word')
        current_word = None
        current_idx = 0
        if word_id:
            for i, w in enumerate(words):
                if str(w.id) == word_id:
                    current_word = w
                    current_idx = i
                    break
        if not current_word:
            current_word = words[0]
            current_idx = 0
        revealed = request.GET.get('revealed') == '1'
        prev_word = words[current_idx - 1] if current_idx > 0 else None
        next_word = words[current_idx + 1] if current_idx < total - 1 else None
        current = current_idx + 1

    base_params = {}
    if cat: base_params['cat'] = cat
    if level: base_params['level'] = level
    if count: base_params['count'] = count
    base_qs = urllib.parse.urlencode(base_params)

    return render(request, 'vocabulary/study_custom.html', {
        'categories': categories,
        'levels': levels,
        'cat': cat,
        'level': level,
        'count': str(count),
        'words': words,
        'word': current_word,
        'current': current if words else 0,
        'total': total,
        'prev_word': prev_word if words else None,
        'next_word': next_word if words else None,
        'revealed': revealed if words else False,
        'base_qs': base_qs,
    })

def category_list(request):
    categories = Category.objects.annotate(word_count=Count('words'))
    return render(request, 'vocabulary/categories.html', {'categories': categories})

def category_detail(request, slug):
    category = get_object_or_404(Category.objects.annotate(word_count=Count('words')), slug=slug)
    words = category.words.all()
    return render(request, 'vocabulary/detail.html', {'category': category, 'words': words})

def study_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    words = list(category.words.all())
    total = len(words)
    if total == 0:
        return redirect('category_detail', slug=slug)

    word_id = request.GET.get('word')
    current_word = None
    current_idx = 0
    if word_id:
        for i, w in enumerate(words):
            if str(w.id) == word_id:
                current_word = w
                current_idx = i
                break
    if not current_word:
        current_word = words[0]
        current_idx = 0

    revealed = request.GET.get('revealed') == '1'
    prev_word = words[current_idx - 1] if current_idx > 0 else None
    next_word = words[current_idx + 1] if current_idx < total - 1 else None

    return render(request, 'vocabulary/study.html', {
        'category': category,
        'word': current_word,
        'current': current_idx + 1,
        'total': total,
        'prev_word': prev_word,
        'next_word': next_word,
        'revealed': revealed,
    })

def word_detail(request, pk):
    word = get_object_or_404(Word, pk=pk)
    word_note = ''
    if request.user.is_authenticated:
        prog = UserWordProgress.objects.filter(user=request.user, word=word).first()
        if prog:
            word_note = prog.notes
    return render(request, 'vocabulary/word.html', {'word': word, 'word_note': word_note})

def word_search(request):
    query = request.GET.get('q', '')
    results = Word.objects.filter(
        Q(korean__icontains=query) | Q(russian__icontains=query) | Q(romanization__icontains=query)
    ) if query else []
    return render(request, 'vocabulary/search.html', {'query': query, 'results': results})

@login_required
@require_POST
def add_to_review(request):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json'
    word_id = None
    mark_learned = None
    if request.content_type == 'application/json':
        import json
        try:
            data = json.loads(request.body)
            word_id = data.get('word_id')
            mark_learned = data.get('mark_learned')
        except json.JSONDecodeError:
            pass
    else:
        word_id = request.POST.get('word_id')
        mark_learned = request.POST.get('mark_learned')

    msg = ''
    if word_id:
        prog, created = UserWordProgress.objects.get_or_create(
            user=request.user, word_id=word_id,
            defaults={'next_review': timezone.now()}
        )
        if mark_learned:
            prog.learned = True
            if not prog.learned_at:
                prog.learned_at = timezone.now()
            prog.save(update_fields=['learned', 'learned_at'])
            msg = '✅ Слово отмечено как выученное!'
            if not is_ajax:
                messages.success(request, msg)
        elif not created and prog.learned:
            prog.learned = False
            prog.next_review = timezone.now()
            prog.save(update_fields=['learned', 'next_review'])
            msg = '🔄 Слово добавлено в повторение'
            if not is_ajax:
                messages.success(request, msg)
        elif created:
            msg = '🔄 Слово добавлено в повторение'
            if not is_ajax:
                messages.success(request, msg)

    if is_ajax:
        return JsonResponse({'success': True, 'message': msg})
    return redirect(request.META.get('HTTP_REFERER', 'category_list'))

@login_required
def word_list_list(request):
    lists = WordList.objects.filter(user=request.user).annotate(word_count=Count('words'))
    return render(request, 'vocabulary/lists.html', {'lists': lists})

@login_required
def word_list_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            WordList.objects.create(user=request.user, name=name)
            messages.success(request, f'📋 Коллекция "{name}" создана')
            return redirect('word_list_list')
    return render(request, 'vocabulary/list_create.html')

@login_required
def word_list_detail(request, pk):
    wl = get_object_or_404(WordList.objects.annotate(word_count=Count('words')), pk=pk, user=request.user)
    words = list(wl.words.all())
    return render(request, 'vocabulary/list_detail.html', {'word_list': wl, 'words': words, 'word_count': len(words)})

@login_required
def word_list_study(request, pk):
    wl = get_object_or_404(WordList, pk=pk, user=request.user)
    words = list(wl.words.all())
    total = len(words)
    if total == 0:
        return redirect('word_list_detail', pk=pk)

    word_id = request.GET.get('word')
    current_word = None
    current_idx = 0
    if word_id:
        for i, w in enumerate(words):
            if str(w.id) == word_id:
                current_word = w
                current_idx = i
                break
    if not current_word:
        current_word = words[0]
        current_idx = 0

    revealed = request.GET.get('revealed') == '1'
    prev_word = words[current_idx - 1] if current_idx > 0 else None
    next_word = words[current_idx + 1] if current_idx < total - 1 else None

    return render(request, 'vocabulary/list_study.html', {
        'word_list': wl,
        'word': current_word,
        'current': current_idx + 1,
        'total': total,
        'prev_word': prev_word,
        'next_word': next_word,
        'revealed': revealed,
    })

@login_required
def word_list_export(request, pk):
    wl = get_object_or_404(WordList, pk=pk, user=request.user)
    safe_name = re.sub(r'[^\w\s\-]', '', wl.name).strip()[:50] or 'words'
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{safe_name}.csv"'
    response.write('\ufeff')
    writer = csv.writer(response)
    writer.writerow(['Корейский', 'Русский', 'Романизация', 'Категория', 'Уровень', 'Пример'])
    for word in wl.words.all():
        writer.writerow([word.korean, word.russian, word.romanization, word.category.name, word.get_level_display(), word.example_sentence])
    return response

@login_required
@require_POST
def word_list_add_word(request, pk, word_id):
    wl = get_object_or_404(WordList, pk=pk, user=request.user)
    word = get_object_or_404(Word, pk=word_id)
    wl.words.add(word)
    msg = f'✅ {word.korean} добавлен в "{wl.name}"'
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    if is_ajax:
        return JsonResponse({'success': True, 'message': msg})
    messages.success(request, msg)
    return redirect(request.META.get('HTTP_REFERER', 'word_list_list'))

@login_required
@require_POST
def save_word_note(request, pk):
    notes = request.POST.get('notes', '')
    prog, _ = UserWordProgress.objects.get_or_create(
        user=request.user, word_id=pk,
        defaults={'next_review': timezone.now()}
    )
    prog.notes = notes
    prog.save(update_fields=['notes'])
    messages.success(request, '📝 Заметка сохранена')
    return redirect(request.META.get('HTTP_REFERER', 'category_list'))

@login_required
@require_POST
def word_list_remove_word(request, pk, word_id):
    wl = get_object_or_404(WordList, pk=pk, user=request.user)
    word = get_object_or_404(Word, pk=word_id)
    wl.words.remove(word)
    return redirect('word_list_detail', pk=pk)


