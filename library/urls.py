from django.urls import path
from . import views

urlpatterns = [
    path('', views.library_index, name='library_index'),
    path('random/', views.library_random, name='library_random'),
    path('search/', views.library_search, name='library_search'),
    path('bookmarks/', views.library_bookmarks, name='library_bookmarks'),
    path('api/word-lookup/', views.api_word_lookup, name='api_word_lookup'),
    path('api/add-to-vocab/', views.api_add_to_vocab, name='api_add_to_vocab'),
    path('api/highlights/', views.api_highlights_list, name='api_highlights'),
    path('api/highlight/toggle/', views.api_highlight_toggle, name='api_highlight_toggle'),
    path('api/highlight/update/', views.api_highlight_update, name='api_highlight_update'),
    path('api/highlight/delete/', views.api_highlight_delete, name='api_highlight_delete'),
    path('api/bookmark/update/', views.api_bookmark_update, name='api_bookmark_update'),
    path('api/bookmark/delete/', views.api_bookmark_delete, name='api_bookmark_delete'),
    path('highlights/', views.library_highlights, name='library_highlights'),
    path('generate-quiz/<str:slug>/', views.library_generate_quiz, name='library_generate_quiz'),
    path('reader/<str:slug>/', views.library_reader, name='library_reader'),
    path('<str:slug>/', views.library_detail, name='library_detail'),
]
