from django.shortcuts import render
from django.http import JsonResponse
from django.core.cache import cache
from django.views.decorators.http import require_GET
from gtts import gTTS
import os
import re
import hmac
import hashlib
import tempfile
from django.conf import settings
from django.utils import timezone

from vocabulary.models import Word

CONSONANTS = [
    ('ㄱ', 'g/k'), ('ㄴ', 'n'), ('ㄷ', 'd/t'), ('ㄹ', 'r/l'), ('ㅁ', 'm'),
    ('ㅂ', 'b/p'), ('ㅅ', 's'), ('ㅇ', 'ng'), ('ㅈ', 'j'), ('ㅊ', 'ch'),
    ('ㅋ', 'k'), ('ㅌ', 't'), ('ㅍ', 'p'), ('ㅎ', 'h'),
]

VOWELS = [
    ('ㅏ', 'a'), ('ㅑ', 'ya'), ('ㅓ', 'eo'), ('ㅕ', 'yeo'), ('ㅗ', 'o'),
    ('ㅛ', 'yo'), ('ㅜ', 'u'), ('ㅠ', 'yu'), ('ㅡ', 'eu'), ('ㅣ', 'i'),
    ('ㅐ', 'ae'), ('ㅒ', 'yae'), ('ㅔ', 'e'), ('ㅖ', 'ye'), ('ㅘ', 'wa'),
    ('ㅚ', 'oe'), ('ㅙ', 'wae'), ('ㅝ', 'wo'), ('ㅞ', 'we'), ('ㅟ', 'wi'),
    ('ㅢ', 'ui'),
]

BATCHIM = [
    ('ㄱ', 'k'), ('ㄲ', 'kk'), ('ㄳ', 'ks'), ('ㄴ', 'n'), ('ㄵ', 'nj'),
    ('ㄶ', 'nh'), ('ㄷ', 't'), ('ㄹ', 'l'), ('ㄺ', 'lk'), ('ㄻ', 'lm'),
    ('ㄼ', 'lb'), ('ㄽ', 'ls'), ('ㄾ', 'lt'), ('ㄿ', 'lp'), ('ㅀ', 'lh'),
    ('ㅁ', 'm'), ('ㅂ', 'p'), ('ㅄ', 'ps'), ('ㅅ', 't'), ('ㅆ', 'ss'),
    ('ㅇ', 'ng'), ('ㅈ', 't'), ('ㅊ', 't'), ('ㅋ', 'k'), ('ㅌ', 't'),
    ('ㅍ', 'p'), ('ㅎ', 't'),
]

def hangul_page(request):
    return render(request, 'hangul/index.html', {
        'consonants': CONSONANTS,
        'vowels': VOWELS,
        'batchim': BATCHIM,
    })


TTS_MAX_TEXT_LEN = 200
TTS_RATE_LIMIT = 30
TTS_RATE_WINDOW = 60


def _client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


@require_GET
def tts_audio(request):
    text = request.GET.get('text', '').strip()
    if not text:
        return JsonResponse({'error': 'No text'}, status=400)
    if len(text) > TTS_MAX_TEXT_LEN:
        return JsonResponse({'error': 'Text too long'}, status=400)

    # Rate limit: sliding window per IP, stored server-side in the cache
    ip = _client_ip(request)
    cache_key = f'tts_rl_{hmac.new(settings.SECRET_KEY.encode(), ip.encode(), hashlib.sha256).hexdigest()[:16]}'
    now_ts = timezone.now().timestamp()
    timestamps = [t for t in cache.get(cache_key, []) if now_ts - t < TTS_RATE_WINDOW]
    if len(timestamps) >= TTS_RATE_LIMIT:
        return JsonResponse({'error': 'Rate limit. Try again later.'}, status=429)
    timestamps.append(now_ts)
    cache.set(cache_key, timestamps, TTS_RATE_WINDOW)

    # Unguessable cache filename: keyed by text via HMAC-SECRET_KEY (not reversible)
    token = hmac.new(settings.SECRET_KEY.encode(), text.encode(), hashlib.sha256).hexdigest()[:32]
    filename = f'{token}.mp3'
    tts_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
    os.makedirs(tts_dir, exist_ok=True)
    filepath = os.path.join(tts_dir, filename)

    if not os.path.exists(filepath):
        try:
            tts = gTTS(text=text, lang='ko')
            fd, tmp_path = tempfile.mkstemp(suffix='.tmp', dir=tts_dir)
            try:
                with os.fdopen(fd, 'wb') as f:
                    tts.write_to_fp(f)
                os.replace(tmp_path, filepath)
            except Exception:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                raise
        except Exception:
            return JsonResponse({'error': 'TTS generation failed'}, status=502)
    return JsonResponse({'url': f'{settings.MEDIA_URL}tts/{filename}'})

def sentence_builder(request):
    from vocabulary.models import Category
    words = Word.objects.select_related('category').all().order_by('category__name', 'korean')
    categories = Category.objects.all().order_by('name')
    word_bank = [
        {
            'id': w.id,
            'korean': w.korean,
            'russian': w.russian,
            'category': w.category.name,
            'category_slug': w.category.slug,
            'level': w.level,
        }
        for w in words
    ]
    return render(request, 'hangul/builder.html', {
        'word_bank': word_bank,
        'categories': categories,
    })

SAMPLE_SENTENCES = [
    ("저는 한국어를 공부해요", "Я учу корейский", "beginner"),
    ("친구와 영화를 봤어요", "Смотрел фильм с другом", "elementary"),
    ("내일 도서관에서 책을 읽을 거예요", "Завтра буду читать книгу в библиотеке", "elementary"),
    ("어제 맛있는 김치를 먹었어요", "Вчера ел вкусное кимчи", "beginner"),
    ("날씨가 좋아서 공원에 가고 싶어요", "Погода хорошая, хочу пойти в парк", "elementary"),
    ("한국어가 재미있지만 어려워요", "Корейский интересный, но трудный", "beginner"),
    ("오빠가 커피를 마시면서 신문을 읽어요", "Старший брат пьёт кофе и читает газету", "elementary"),
    ("겨울에 눈이 오면 스키를 타러 가요", "Зимой, когда идёт снег, еду кататься на лыжах", "intermediate"),
]

BREAKDOWN_MAX_LEN = 300
BREAKDOWN_MAX_WORDS = 50


def sentence_breakdown(request):
    result = []
    input_sentence = ''

    if request.method == 'POST':
        input_sentence = request.POST.get('sentence', '').strip()[:BREAKDOWN_MAX_LEN]
        if input_sentence:
            words = re.split(r'[\s,.-]+', input_sentence)
            for w in words[:BREAKDOWN_MAX_WORDS]:
                # Strip LIKE wildcards so user input can't match everything
                w = w.replace('%', '').replace('_', '')
                if not w:
                    continue
                matches = Word.objects.filter(korean__contains=w).select_related('category')[:3]
                if matches:
                    result.append({
                        'word': w,
                        'matches': [
                            {'korean': m.korean, 'russian': m.russian, 'category': m.category.name}
                            for m in matches
                        ]
                    })
                else:
                    result.append({'word': w, 'matches': None})

    return render(request, 'hangul/breakdown.html', {
        'result': result,
        'input_sentence': input_sentence,
        'samples': SAMPLE_SENTENCES,
    })
