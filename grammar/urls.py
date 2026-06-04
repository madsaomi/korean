from django.urls import path
from . import views

app_name = 'grammar'

urlpatterns = [
    path('', views.grammar_list, name='grammar_list'),
    path('exercises/', views.exercise_list, name='exercise_list'),
    path('exercises/start/', views.start_exercise, name='start_exercise'),
    path('exercises/do/', views.do_exercise, name='do_exercise'),
    path('exercises/result/', views.exercise_result, name='exercise_result'),
    path('<slug:slug>/', views.grammar_detail, name='grammar_detail'),
]
