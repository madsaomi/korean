import os
import time
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Delete cached TTS mp3 files older than the given number of days.'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=7,
                            help='Delete files not modified within this many days (default: 7)')
        parser.add_argument('--dry-run', action='store_true',
                            help='Only show what would be deleted')

    def handle(self, *args, **options):
        days = options['days']
        if days < 0:
            self.stderr.write('--days must be >= 0')
            return

        tts_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
        if not os.path.isdir(tts_dir):
            self.stdout.write('No tts directory — nothing to clean.')
            return

        cutoff = time.time() - days * 86400
        deleted = 0
        kept = 0
        freed_bytes = 0
        for name in os.listdir(tts_dir):
            path = os.path.join(tts_dir, name)
            if not os.path.isfile(path):
                continue
            try:
                mtime = os.path.getmtime(path)
                size = os.path.getsize(path)
            except OSError:
                continue
            if mtime < cutoff:
                if options['dry_run']:
                    self.stdout.write(f'would delete {name}')
                else:
                    try:
                        os.remove(path)
                    except OSError as e:
                        self.stderr.write(f'failed to remove {name}: {e}')
                        continue
                deleted += 1
                freed_bytes += size
            else:
                kept += 1

        verb = 'Would free' if options['dry_run'] else 'Freed'
        self.stdout.write(
            f'Deleted: {deleted}, kept: {kept}. {verb} {freed_bytes / 1024:.1f} KB.'
        )
