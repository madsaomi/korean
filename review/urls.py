from django.urls import path
from . import views

urlpatterns = [
    path('', views.review_page, name='review'),
    path('flashcard/', views.flashcard_mode, name='flashcard'),
]
