import re
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from library.models import LibraryPage

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


class Command(BaseCommand):
    help = 'Импортирует Markdown-файлы в базу данных как LibraryPage'

    def add_arguments(self, parser):
        parser.add_argument('--dir', type=str, default=None, help='Путь к папке с .md файлами')
        parser.add_argument('--language', type=str, default='ko', choices=['ko', 'ja'],
                            help='Язык: ko (Корейский) или ja (Японский)')

    def handle(self, *args, **options):
        lang = options['language']
        default_dir = 'Корейский' if lang == 'ko' else 'Японский'
        if options['dir']:
            lib_dir = Path(options['dir'])
        elif lang == 'ko' and hasattr(settings, 'LIBRARY_DIR'):
            lib_dir = settings.LIBRARY_DIR
        else:
            lib_dir = settings.BASE_DIR / default_dir

        if not lib_dir.exists():
            self.stderr.write(f'Папка {lib_dir} не найдена')
            return

        md_files = sorted(lib_dir.glob('*.md'))
        if not md_files:
            self.stderr.write(f'В папке {lib_dir} нет .md файлов')
            return

        icons = ICONS.get(lang, {})
        descriptions = DESCRIPTIONS.get(lang, {})

        for order, f in enumerate(md_files, start=1):
            slug = f.stem
            name_clean = re.sub(r'^\d+_', '', f.stem)
            icon = '📄'
            for key, val in icons.items():
                if key in name_clean.lower():
                    icon = val
                    break
            desc = ''
            for key, val in descriptions.items():
                if key in name_clean.lower():
                    desc = val
                    break
            md_text = f.read_text(encoding='utf-8')
            word_count = len(md_text.split())
            read_time = max(1, round(word_count / 200))

            page, created = LibraryPage.objects.update_or_create(
                language=lang, slug=slug,
                defaults={
                    'name': name_clean,
                    'icon': icon,
                    'description': desc,
                    'content': md_text,
                    'order': order,
                    'word_count': word_count,
                    'read_time': read_time,
                }
            )
            status = 'создан' if created else 'обновлён'
            self.stdout.write(f'[OK] {page.name} ({slug}) - {status}')

        self.stdout.write(f'Импортировано {len(md_files)} страниц(ы) для языка {lang}')
