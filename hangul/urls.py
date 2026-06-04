from django.urls import path
from . import views

urlpatterns = [
    path('', views.hangul_page, name='hangul'),
    path('tts/', views.tts_audio, name='tts_audio'),
    path('breakdown/', views.sentence_breakdown, name='sentence_breakdown'),
    path('builder/', views.sentence_builder, name='sentence_builder'),
]
