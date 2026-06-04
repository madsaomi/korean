import os
import re
import markdown
from django.shortcuts import render
from django.http import Http404
from django.conf import settings

ICONS = {
    'введение': '📖',
    'хангыль': '🔤',
    'грамматика': '📝',
    'лексика': '📚',
    'фразы': '💬',
    'культура': '🎎',
    'словарь': '📖',
    'ресурсы': '🔗',
}

DESCRIPTIONS = {
    'введение': 'Общая информация о корейском языке, история и мотивация',
    'хангыль': 'Корейский алфавит: согласные, гласные, структура слогов',
    'грамматика': 'Частицы, глаголы, прилагательные, времена и конструкции',
    'лексика': 'Словарный запас по темам: еда, числа, семья и др.',
    'фразы': 'Полезные фразы и диалоги для повседневного общения',
    'культура': 'Корейская культура, праздники, традиции и этикет',
    'словарь': 'Большой корейско-русский словарь по категориям',
    'ресурсы': 'Полезные ссылки, приложения и материалы для изучения',
}


def _get_library_dir():
    return getattr(settings, 'LIBRARY_DIR', settings.BASE_DIR / 'Корейский')


def _get_files():
    lib_dir = _get_library_dir()
    if not lib_dir.exists():
        return []
    files = []
    for f in sorted(lib_dir.iterdir()):
        if f.suffix == '.md':
            slug = f.stem
            name_clean = re.sub(r'^\d+_', '', f.stem)
            icon = '📄'
            for key, val in ICONS.items():
                if key in name_clean.lower():
                    icon = val
                    break
            desc = ''
            for key, val in DESCRIPTIONS.items():
                if key in name_clean.lower():
                    desc = val
                    break
            size_kb = f.stat().st_size / 1024
            files.append({
                'slug': slug,
                'name': name_clean,
                'icon': icon,
                'description': desc,
                'size_kb': round(size_kb, 1),
                'path': f,
            })
    return files


def _extract_toc(md_text):
    """Extract ## and ### headings for table of contents."""
    toc = []
    for line in md_text.split('\n'):
        m = re.match(r'^(#{2,3})\s+(.+)', line)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            anchor = re.sub(r'[^\w\s가-힣а-яёА-ЯЁ-]', '', title)
            anchor = re.sub(r'\s+', '-', anchor).lower()
            toc.append({'level': level, 'title': title, 'anchor': anchor})
    return toc


def library_index(request):
    files = _get_files()
    return render(request, 'library/index.html', {'files': files})


def library_detail(request, slug):
    files = _get_files()
    current = None
    current_idx = -1
    for i, f in enumerate(files):
        if f['slug'] == slug:
            current = f
            current_idx = i
            break
    if not current:
        raise Http404('Файл не найден')

    md_text = current['path'].read_text(encoding='utf-8')
    toc = _extract_toc(md_text)

    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc', 'nl2br'])
    html_content = md.convert(md_text)

    prev_file = files[current_idx - 1] if current_idx > 0 else None
    next_file = files[current_idx + 1] if current_idx < len(files) - 1 else None

    return render(request, 'library/detail.html', {
        'file': current,
        'html_content': html_content,
        'toc': toc,
        'prev_file': prev_file,
        'next_file': next_file,
        'files': files,
    })
