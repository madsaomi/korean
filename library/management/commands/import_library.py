import re, json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from library.models import LibraryPage

ICONS = {
    'введение': '📖', 'хангыль': '🔤', 'грамматика': '📝',
    'лексика': '📚', 'фразы': '💬', 'культура': '🎎',
    'словарь': '📖', 'ресурсы': '🔗',
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


class Command(BaseCommand):
    help = 'Импортирует Markdown-файлы из Корейский/ в базу данных как LibraryPage'

    def add_arguments(self, parser):
        parser.add_argument('--dir', type=str, default=None, help='Путь к папке с .md файлами')

    def handle(self, *args, **options):
        lib_dir = Path(options['dir']) if options['dir'] else getattr(settings, 'LIBRARY_DIR', settings.BASE_DIR / 'Корейский')
        if not lib_dir.exists():
            self.stderr.write(f'Папка {lib_dir} не найдена')
            return

        md_files = sorted(lib_dir.glob('*.md'))
        if not md_files:
            self.stderr.write(f'В папке {lib_dir} нет .md файлов')
            return

        for order, f in enumerate(md_files, start=1):
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
            md_text = f.read_text(encoding='utf-8')
            word_count = len(md_text.split())
            read_time = max(1, round(word_count / 200))

            page, created = LibraryPage.objects.update_or_create(
                slug=slug,
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

        self.stdout.write(f'Импортировано {len(md_files)} страниц(ы)')
