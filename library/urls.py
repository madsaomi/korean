from django.urls import path
from . import views

LANG_DISPLAY = {'korean': 'ko', 'japanese': 'ja'}

# Shared URL patterns for each language
_lang_urls = [
    ('', views.library_index, 'index'),
    ('random/', views.library_random, 'random'),
    ('search/', views.library_search, 'search'),
    ('bookmarks/', views.library_bookmarks, 'bookmarks'),
    ('highlights/', views.library_highlights, 'highlights'),
    ('api/word-lookup/', views.api_word_lookup, 'api_word_lookup'),
    ('api/add-to-vocab/', views.api_add_to_vocab, 'api_add_to_vocab'),
    ('api/highlights/', views.api_highlights_list, 'api_highlights'),
    ('api/highlight/toggle/', views.api_highlight_toggle, 'api_highlight_toggle'),
    ('api/highlight/update/', views.api_highlight_update, 'api_highlight_update'),
    ('api/highlight/delete/', views.api_highlight_delete, 'api_highlight_delete'),
    ('api/bookmark/update/', views.api_bookmark_update, 'api_bookmark_update'),
    ('api/bookmark/delete/', views.api_bookmark_delete, 'api_bookmark_delete'),
    ('generate-quiz/<str:slug>/', views.library_generate_quiz, 'generate_quiz'),
    ('reader/<str:slug>/', views.library_reader, 'reader'),
    ('<str:slug>/', views.library_detail, 'detail'),
]

urlpatterns = [
    path('', views.library_home, name='library_home'),
]

for lang_name, lang_code in LANG_DISPLAY.items():
    for url_suffix, view_func, name_suffix in _lang_urls:
        urlpatterns.append(
            path(f'{lang_name}/{url_suffix}', view_func, {'lang_code': lang_code},
                 name=f'library_{lang_code}_{name_suffix}')
        )

# Old-style URLs → redirect to Korean (backward compat)
for url_suffix, view_func, name_suffix in _lang_urls:
    if name_suffix == 'detail':
        continue
    urlpatterns.append(
        path(url_suffix, view_func, {'lang_code': 'ko'}, name=f'library_{name_suffix}')
    )

# Old detail URL must be LAST (catch-all) and redirect to Korean
urlpatterns.append(
    path('<str:slug>/', views.library_detail_old, name='library_detail_old')
)
