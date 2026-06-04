from django.shortcuts import render
from django.http import JsonResponse
from gtts import gTTS
import os
import hashlib
from django.conf import settings

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

import re
from vocabulary.models import Word

def tts_audio(request):
    text = request.GET.get('text', '')
    if not text:
        return JsonResponse({'error': 'No text'}, status=400)
    filename = f'{hashlib.md5(text.encode()).hexdigest()}.mp3'
    tts_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
    os.makedirs(tts_dir, exist_ok=True)
    filepath = os.path.join(tts_dir, filename)
    if not os.path.exists(filepath):
        tts = gTTS(text=text, lang='ko')
        tts.save(filepath)
    return JsonResponse({'url': f'{settings.MEDIA_URL}tts/{filename}'})

def sentence_builder(request):
    import random
    all_words = list(Word.objects.select_related('category')[:100])
    random.shuffle(all_words)
    word_bank = [
        {'id': w.id, 'korean': w.korean, 'russian': w.russian, 'category': w.category.name}
        for w in all_words[:30]
    ]
    return render(request, 'hangul/builder.html', {'word_bank': word_bank})

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

def sentence_breakdown(request):
    result = []
    input_sentence = ''

    if request.method == 'POST':
        input_sentence = request.POST.get('sentence', '').strip()
        if input_sentence:
            words = re.split(r'[\s,.-]+', input_sentence)
            for w in words:
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
