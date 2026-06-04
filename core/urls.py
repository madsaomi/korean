from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.unified_search, name='unified_search'),
    path('random-word/', views.random_word_api, name='random_word_api'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
]
