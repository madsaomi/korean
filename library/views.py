import json, re, random, markdown, bleach
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from .models import LibraryPage, ReadingProgress, Bookmark, Note, Highlight, LibraryTag
from vocabulary.models import Word

KOREAN_RE = re.compile(r'[\uac00-\ud7af\u1100-\u11ff\u3130-\u318f\ua960-\ua97c]+')
HEADING_ID_RE = re.compile(r'<h([2-3])\s*[^>]*>(.*?)</h\1>', re.DOTALL)
KOREAN_BLOCK_RE = re.compile(r'(<p[^>]*>)(.*?)(</p>)', re.DOTALL)


def _get_files():
    return list(LibraryPage.objects.all().order_by('order'))


def _extract_toc(md_text):
    toc = []
    for line in md_text.split('\n'):
        m = re.match(r'^(#{2,3})\s+(.+)', line)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            anchor = re.sub(r'[^\w\s\uac00-\ud7af\u0430-\u044f\u0451\u0410-\u042f\u0401-]', '', title)
            anchor = re.sub(r'\s+', '-', anchor).lower()
            toc.append({'level': level, 'title': title, 'anchor': anchor})
    return toc


def _add_korean_tts_spans(html):
    def wrap_korean(m):
        tag_open = m.group(1)
        content = m.group(2)
        tag_close = m.group(3)

        def replace_korean(text_piece):
            parts = KOREAN_RE.split(text_piece)
            korean_chunks = KOREAN_RE.findall(text_piece)
            result = []
            for i, part in enumerate(parts):
                result.append(part)
                if i < len(korean_chunks):
                    chunk = korean_chunks[i].strip()
                    if len(chunk) >= 2:
                        result.append(f'<span class="korean-tts" data-tts="{chunk}">{chunk}</span>')
                    else:
                        result.append(chunk)
            return ''.join(result)

        return tag_open + replace_korean(content) + tag_close

    return KOREAN_BLOCK_RE.sub(wrap_korean, html)


def _add_heading_ids(html):
    def add_id(m):
        level = m.group(1)
        content = m.group(2)
        anchor = re.sub(r'<[^>]+>', '', content)
        anchor = re.sub(r'[^\w\s\uac00-\ud7af\u0430-\u044f\u0451\u0410-\u042f\u0401-]', '', anchor)
        anchor = re.sub(r'\s+', '-', anchor).lower().strip('-')
        return f'<h{level} id="{anchor}">{content}</h{level}>'

    return HEADING_ID_RE.sub(add_id, html)


def _process_md_html(md_text):
    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc', 'nl2br'])
    html = md.convert(md_text)
    html = _add_heading_ids(html)
    html = _add_korean_tts_spans(html)
    allowed_tags = [
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'hr',
        'ul', 'ol', 'li', 'dl', 'dt', 'dd',
        'table', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td',
        'pre', 'code', 'blockquote', 'cite',
        'a', 'img', 'em', 'i', 'strong', 'b', 'u', 's', 'span', 'div',
        'abbr', 'acronym', 'sub', 'sup',
    ]
    allowed_attrs = {
        'a': ['href', 'title', 'rel'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
        '*': ['id', 'class'],
    }
    html = bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs, strip=True)
    return html


def _search_in_file(file_info, query):
    query_lower = query.lower()
    md_text = file_info.content
    lines = md_text.split('\n')
    results = []
    for i, line in enumerate(lines):
        idx = line.lower().find(query_lower)
        if idx != -1:
            before = line[max(0, idx - 40):idx]
            match = line[idx:idx + len(query)]
            after = line[idx + len(query):idx + len(query) + 40]
            results.append({
                'line_num': i + 1,
                'before': before,
                'match': match,
                'after': after,
            })
    return results


def _get_user_data(user, files):
    if not user.is_authenticated:
        for f in files:
            f.is_read = False
            f.is_bookmarked = False
            f.tags = []
            f.size_kb = round(len(f.content.encode('utf-8')) / 1024, 1)
        return files
    slugs = [f.slug for f in files]
    read_progress = {
        r.slug: r for r in
        ReadingProgress.objects.filter(user=user, slug__in=slugs)
    }
    bookmarks = set(
        Bookmark.objects.filter(user=user, slug__in=slugs)
        .values_list('slug', flat=True)
    )
    tags = {}
    for t in LibraryTag.objects.filter(user=user, slug__in=slugs):
        tags.setdefault(t.slug, []).append(t.tag)
    for f in files:
        f.is_read = f.slug in read_progress and read_progress[f.slug].read
        f.is_bookmarked = f.slug in bookmarks
        f.tags = tags.get(f.slug, [])
        f.size_kb = round(len(f.content.encode('utf-8')) / 1024, 1)
        f.read_progress_obj = read_progress.get(f.slug)
    return files


# ─── Views ────────────────────────────────────────────────────────────────

def library_index(request):
    files = _get_files()
    files = _get_user_data(request.user, files)
    total_read = sum(1 for f in files if f.is_read)
    total_files = len(files)
    query = request.GET.get('q', '')
    return render(request, 'library/index.html', {
        'files': files,
        'total_read': total_read,
        'total_files': total_files,
        'query': query,
    })


def library_random(request):
    files = _get_files()
    if not files:
        return redirect('library_index')
    f = random.choice(files)
    return redirect('library_detail', slug=f.slug)


def library_detail(request, slug):
    current = get_object_or_404(LibraryPage, slug=slug)
    current.size_kb = round(len(current.content.encode('utf-8')) / 1024, 1)
    files = _get_files()
    current_idx = next((i for i, f in enumerate(files) if f.slug == slug), -1)

    toc = _extract_toc(current.content)
    html_content = _process_md_html(current.content)

    prev_file = files[current_idx - 1] if current_idx > 0 else None
    next_file = files[current_idx + 1] if current_idx < len(files) - 1 else None

    ctx = {
        'file': current,
        'html_content': html_content,
        'toc': toc,
        'prev_file': prev_file,
        'next_file': next_file,
        'files': files,
    }

    if request.method == 'POST':
        action = request.POST.get('action')
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'auth_required'}, status=403)
        if action == 'toggle_read':
            prog, _ = ReadingProgress.objects.get_or_create(
                user=request.user, slug=slug)
            prog.read = not prog.read
            prog.read_at = timezone.now() if prog.read else None
            prog.save(update_fields=['read', 'read_at'])
            return JsonResponse({'read': prog.read})
        elif action == 'toggle_bookmark':
            bm, created = Bookmark.objects.get_or_create(
                user=request.user, slug=slug,
                defaults={'title': current.name, 'anchor': ''})
            if not created:
                bm.delete()
                return JsonResponse({'bookmarked': False})
            return JsonResponse({'bookmarked': True})
        elif action == 'save_note':
            highlighted = request.POST.get('highlighted', '')
            content = request.POST.get('content', '')
            anchor = request.POST.get('anchor', '')
            note = Note.objects.create(
                user=request.user, slug=slug,
                anchor=anchor, highlighted_text=highlighted,
                content=content)
            return JsonResponse({
                'id': note.id,
                'highlighted_text': note.highlighted_text,
                'content': note.content,
                'created_at': note.created_at.isoformat(),
            })
        elif action == 'delete_note':
            note_id = request.POST.get('note_id')
            Note.objects.filter(id=note_id, user=request.user).delete()
            return JsonResponse({'deleted': True})
        elif action == 'add_tag':
            tag = request.POST.get('tag', '').strip().lower()
            if tag:
                LibraryTag.objects.get_or_create(
                    user=request.user, slug=slug, tag=tag)
            return JsonResponse({'tags': list(
                LibraryTag.objects.filter(user=request.user, slug=slug)
                .values_list('tag', flat=True))})
        elif action == 'remove_tag':
            tag = request.POST.get('tag', '').strip().lower()
            LibraryTag.objects.filter(
                user=request.user, slug=slug, tag=tag).delete()
            return JsonResponse({'tags': list(
                LibraryTag.objects.filter(user=request.user, slug=slug)
                .values_list('tag', flat=True))})
        return JsonResponse({'error': 'unknown_action'}, status=400)

    if request.user.is_authenticated:
        prog = ReadingProgress.objects.filter(
            user=request.user, slug=slug).first()
        ctx['is_read'] = prog.read if prog else False
        ctx['is_bookmarked'] = Bookmark.objects.filter(
            user=request.user, slug=slug).exists()
        ctx['notes'] = list(Note.objects.filter(
            user=request.user, slug=slug).values(
            'id', 'highlighted_text', 'content', 'anchor', 'created_at'))
        ctx['tags'] = list(LibraryTag.objects.filter(
            user=request.user, slug=slug).values_list('tag', flat=True))
        ctx['total_read'] = ReadingProgress.objects.filter(
            user=request.user, read=True).count()
    else:
        ctx['is_read'] = ctx['is_bookmarked'] = False
        ctx['notes'] = []
        ctx['tags'] = []
        ctx['total_read'] = 0
    ctx['total_files'] = len(files)

    return render(request, 'library/detail.html', ctx)


def library_search(request):
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        files = _get_files()
        for f in files:
            matches = _search_in_file(f, query)
            if matches:
                results.append({
                    'file': f,
                    'matches': matches,
                    'match_count': len(matches),
                })
        results.sort(key=lambda r: -r['match_count'])
    return render(request, 'library/search.html', {
        'query': query,
        'results': results,
    })


def library_reader(request, slug):
    current = get_object_or_404(LibraryPage, slug=slug)
    current.size_kb = round(len(current.content.encode('utf-8')) / 1024, 1)
    files = _get_files()
    current_idx = next((i for i, f in enumerate(files) if f.slug == slug), -1)

    toc = _extract_toc(current.content)
    html_content = _process_md_html(current.content)
    prev_file = files[current_idx - 1] if current_idx > 0 else None
    next_file = files[current_idx + 1] if current_idx < len(files) - 1 else None

    return render(request, 'library/reader.html', {
        'file': current,
        'html_content': html_content,
        'toc': toc,
        'prev_file': prev_file,
        'next_file': next_file,
    })


def library_bookmarks(request):
    if not request.user.is_authenticated:
        return redirect('login')
    bookmarks = Bookmark.objects.filter(user=request.user)
    return render(request, 'library/bookmarks.html', {
        'bookmarks': bookmarks,
    })


@login_required
def api_word_lookup(request):
    word_text = request.GET.get('word', '').strip()
    if not word_text:
        return JsonResponse({'found': False})
    word = Word.objects.filter(
        Q(korean__iexact=word_text) | Q(korean__icontains=word_text)
    ).first()
    if word:
        from progress.models import UserWordProgress
        in_vocab = UserWordProgress.objects.filter(
            user=request.user, word=word).exists()
        return JsonResponse({
            'found': True,
            'id': word.id,
            'korean': word.korean,
            'russian': word.russian,
            'romanization': word.romanization,
            'example': word.example_sentence or '',
            'example_tr': word.example_translation or '',
            'in_vocab': in_vocab,
        })
    return JsonResponse({'found': False})


@login_required
def api_add_to_vocab(request):
    word_id = request.POST.get('word_id')
    if not word_id:
        return JsonResponse({'success': False}, status=400)
    from progress.models import UserWordProgress
    word = get_object_or_404(Word, id=word_id)
    prog, created = UserWordProgress.objects.get_or_create(
        user=request.user, word=word)
    if created:
        prog.next_review = timezone.now()
        prog.save(update_fields=['next_review'])
    return JsonResponse({'success': True, 'in_vocab': True})


# ─── Highlight API ─────────────────────────────────────────────────────────

def api_highlights_list(request):
    if not request.user.is_authenticated:
        return JsonResponse({'highlights': []})
    slug = request.GET.get('slug', '')
    if not slug:
        qs = Highlight.objects.filter(user=request.user).values(
            'id', 'text', 'color', 'slug', 'note', 'anchor', 'start_offset', 'end_offset', 'created_at').order_by('-created_at')
        return JsonResponse({'highlights': list(qs)})
    qs = Highlight.objects.filter(user=request.user, slug=slug).values(
        'id', 'text', 'color', 'note', 'anchor', 'start_offset', 'end_offset', 'created_at')
    return JsonResponse({'highlights': list(qs)})


@login_required
def api_highlight_toggle(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    slug = request.POST.get('slug', '')
    text = request.POST.get('text', '').strip()
    if not slug or not text:
        return JsonResponse({'error': 'missing fields'}, status=400)
    start_off = int(request.POST.get('start_offset', 0))
    end_off = int(request.POST.get('end_offset', 0))
    existing = Highlight.objects.filter(
        user=request.user, slug=slug, text=text, start_offset=start_off, end_offset=end_off)
    if existing.exists():
        existing.delete()
        return JsonResponse({'highlighted': False, 'id': None})
    hl = Highlight.objects.create(
        user=request.user,
        slug=slug,
        anchor=request.POST.get('anchor', ''),
        text=text,
        color=request.POST.get('color', 'yellow'),
        note=request.POST.get('note', ''),
        start_offset=start_off,
        end_offset=end_off,
    )
    return JsonResponse({'highlighted': True, 'id': hl.id})


@login_required
def api_highlight_update(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    hl_id = request.POST.get('id')
    if not hl_id:
        return JsonResponse({'error': 'missing id'}, status=400)
    hl = get_object_or_404(Highlight, id=hl_id, user=request.user)
    if request.POST.get('note') is not None:
        hl.note = request.POST['note']
    if request.POST.get('color'):
        hl.color = request.POST['color']
    hl.save(update_fields=['note', 'color'])
    return JsonResponse({'updated': True, 'id': hl.id})


@login_required
def api_highlight_delete(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    hl_id = request.POST.get('id')
    if not hl_id:
        return JsonResponse({'error': 'missing id'}, status=400)
    deleted, _ = Highlight.objects.filter(id=hl_id, user=request.user).delete()
    return JsonResponse({'deleted': bool(deleted)})


# ─── Bookmark API ─────────────────────────────────────────────────────────

@login_required
def api_bookmark_update(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    bm_id = request.POST.get('id')
    if bm_id:
        bm = get_object_or_404(Bookmark, id=bm_id, user=request.user)
        if request.POST.get('note') is not None:
            bm.note = request.POST['note']
        if request.POST.get('color'):
            bm.color = request.POST['color']
        bm.save()
        return JsonResponse({'bookmarked': True, 'id': bm.id})
    slug = request.POST.get('slug', '')
    if not slug:
        return JsonResponse({'error': 'missing slug'}, status=400)
    bm, created = Bookmark.objects.get_or_create(
        user=request.user, slug=slug,
        defaults={'title': request.POST.get('title', slug), 'anchor': ''})
    if not created:
        bm.delete()
        return JsonResponse({'bookmarked': False})
    if request.POST.get('color'):
        bm.color = request.POST['color']
    if request.POST.get('section'):
        bm.section = request.POST['section']
    if request.POST.get('note'):
        bm.note = request.POST['note']
    bm.save()
    return JsonResponse({'bookmarked': True, 'id': bm.id})


@login_required
def api_bookmark_delete(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    bm_id = request.POST.get('id')
    if not bm_id:
        return JsonResponse({'error': 'missing id'}, status=400)
    deleted, _ = Bookmark.objects.filter(id=bm_id, user=request.user).delete()
    return JsonResponse({'deleted': bool(deleted)})


# ─── Highlights summary view ──────────────────────────────────────────────

@login_required
def library_highlights(request):
    highlights = Highlight.objects.filter(user=request.user).order_by('-created_at').values(
        'id', 'slug', 'text', 'color', 'note', 'anchor', 'created_at')
    page_slugs = set(h['slug'] for h in highlights)
    pages = {p.slug: p for p in LibraryPage.objects.filter(slug__in=page_slugs)}
    for h in highlights:
        page = pages.get(h['slug'])
        h['page_name'] = page.name if page else h['slug']
        h['page_icon'] = page.icon if page else '📄'
    return render(request, 'library/highlights.html', {'highlights': highlights})


def library_generate_quiz(request, slug):
    current = get_object_or_404(LibraryPage, slug=slug)
    md_text = current.content
    lines = md_text.split('\n')

    questions = []
    headings = []
    for line in lines:
        m = re.match(r'^(#{2,3})\s+(.+)', line)
        if m:
            headings.append({'level': len(m.group(1)), 'title': m.group(2).strip()})

    bold_items = re.findall(r'\*\*(.+?)\*\*', md_text)
    important = [b for b in bold_items if len(b) > 3 and len(b) < 100]

    for h in headings:
        questions.append({
            'question': f'О чём рассказывается в разделе «{h["title"]}»?',
            'type': 'heading',
            'topic': h['title'],
        })

    if important:
        random.shuffle(important)
        for item in important[:10]:
            questions.append({
                'question': f'Что означает/относится к «{item}»?',
                'type': 'term',
                'term': item,
            })

    random.shuffle(questions)
    questions = questions[:15]

    return render(request, 'library/quiz.html', {
        'file': current,
        'questions': questions,
        'questions_json': json.dumps(questions),
    })
