from django.urls import path
from . import views

urlpatterns = [
    path('', views.library_index, name='library_index'),
    path('<str:slug>/', views.library_detail, name='library_detail'),
]
