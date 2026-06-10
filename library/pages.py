import re
from dataclasses import dataclass
from pathlib import Path
from django.conf import settings

ICONS = {
    'ko': {
        'введение': '📖', 'хангыль': '🔤', 'грамматика': '📝',
        'лексика': '📚', 'фразы': '💬', 'культура': '🎎',
        'словарь': '📖', 'ресурсы': '🔗',
    },
    'ja': {
        'оглавление': '📑', 'введение': '📖', 'хирагана': '🔤',
        'катакана': '🔤', 'кандзи': '🈯', 'грамматика': '📝',
        'прилагат': '🔢', 'числа': '🔢', 'лексика': '📚',
        'фразы': '💬', 'диалоги': '💬', 'приложения': '📎',
        'ошибки': '⚠️', 'jlpt': '🏅', 'культура': '🎎',
        'глоссарий': '📖', 'словарь': '📖', 'ресурсы': '🔗',
    },
}

DESCRIPTIONS = {
    'ko': {
        'введение': 'Общая информация о корейском языке, история и мотивация',
        'хангыль': 'Корейский алфавит: согласные, гласные, структура слогов',
        'грамматика': 'Частицы, глаголы, прилагательные, времена и конструкции',
        'лексика': 'Словарный запас по темам: еда, числа, семья и др.',
        'фразы': 'Полезные фразы и диалоги для повседневного общения',
        'культура': 'Корейская культура, праздники, традиции и этикет',
        'словарь': 'Большой корейско-русский словарь по категориям',
        'ресурсы': 'Полезные ссылки, приложения и материалы для изучения',
    },
    'ja': {
        'оглавление': 'Содержание учебника японского языка',
        'введение': 'Общая информация о японском языке, письменность и особенности',
        'хирагана': 'Хирагана и катакана — слоговая азбука японского языка',
        'кандзи': 'Китайские иероглифы: ключи, чтения и написание',
        'грамматика': 'Грамматика уровней N5 и N4: частицы, глаголы, прилагательные',
        'прилагат': 'Прилагательные, числительные, счётные суффиксы, время и даты',
        'лексика': 'Словарный запас по темам: еда, семья, работа, природа',
        'фразы': 'Полезные фразы и диалоги для повседневного общения',
        'приложения': 'Дополнительные материалы и приложения',
        'ошибки': 'Типичные ошибки изучающих японский язык',
        'jlpt': 'Подготовка к JLPT: структура экзамена, советы, стратегии',
        'культура': 'Японская культура, традиции и глоссарий',
        'словарь': 'Японско-русский словарь по категориям',
        'ресурсы': 'Полезные ссылки, приложения и материалы для изучения',
    },
}


@dataclass
class PageInfo:
    language: str
    slug: str
    name: str
    icon: str
    description: str
    content: str
    order: int
    word_count: int
    read_time: int

    @property
    def size_kb(self):
        return round(len(self.content.encode('utf-8')) / 1024, 1)


def _get_md_dir(language):
    return settings.BASE_DIR / ('Корейский' if language == 'ko' else 'Японский')


def _parse_frontmatter(text):
    if text.startswith('---'):
        parts = text.split('---', 2)
        if len(parts) >= 3:
            try:
                import yaml
                fm = yaml.safe_load(parts[1]) or {}
                return fm, parts[2].strip()
            except Exception:
                pass
    return {}, text


def _file_to_pageinfo(filepath, language, order):
    text = filepath.read_text(encoding='utf-8')
    fm, body = _parse_frontmatter(text)

    slug = filepath.stem
    name_clean = re.sub(r'^\d+_', '', filepath.stem)

    icon = fm.get('icon', '')
    if not icon:
        icons = ICONS.get(language, {})
        for key, val in icons.items():
            if key in name_clean.lower():
                icon = val
                break
        if not icon:
            icon = '📄'

    description = fm.get('description', '')
    if not description:
        descriptions = DESCRIPTIONS.get(language, {})
        for key, val in descriptions.items():
            if key in name_clean.lower():
                description = val
                break

    word_count = len(body.split())
    read_time = max(1, round(word_count / 200))

    return PageInfo(
        language=language, slug=slug, name=name_clean,
        icon=icon, description=description, content=body,
        order=order, word_count=word_count, read_time=read_time,
    )


def get_all_pages(language='ko'):
    md_dir = _get_md_dir(language)
    if not md_dir.exists():
        return []
    files = sorted(md_dir.rglob('*.md'))
    return [_file_to_pageinfo(f, language, i + 1) for i, f in enumerate(files)]


def get_page(language, slug):
    md_dir = _get_md_dir(language)
    all_files = sorted(md_dir.rglob('*.md'))
    for i, f in enumerate(all_files):
        if f.stem == slug:
            return _file_to_pageinfo(f, language, i + 1)
    return None


def get_page_count(language='ko'):
    md_dir = _get_md_dir(language)
    if not md_dir.exists():
        return 0
    return len(list(md_dir.rglob('*.md')))


def get_pages_by_slugs(language, slugs):
    pages = get_all_pages(language)
    return {p.slug: p for p in pages if p.slug in slugs}
