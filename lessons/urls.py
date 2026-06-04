from django.urls import path
from . import views

urlpatterns = [
    path('', views.lesson_list, name='lesson_list'),
    path('<int:course_id>/', views.lesson_detail, name='lesson_detail'),
    path('<int:course_id>/<int:lesson_id>/', views.lesson_detail, name='lesson_detail_with_id'),
]
