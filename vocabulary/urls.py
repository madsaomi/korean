from django.urls import path
from . import views

urlpatterns = [
    path('', views.category_list, name='category_list'),
    path('study/', views.study_custom, name='study_custom'),
    path('search/', views.word_search, name='word_search'),
    path('add-to-review/', views.add_to_review, name='add_to_review'),
    path('word/<int:pk>/', views.word_detail, name='word_detail'),
    path('lists/', views.word_list_list, name='word_list_list'),
    path('lists/create/', views.word_list_create, name='word_list_create'),
    path('lists/<int:pk>/', views.word_list_detail, name='word_list_detail'),
    path('lists/<int:pk>/add/<int:word_id>/', views.word_list_add_word, name='word_list_add_word'),
    path('lists/<int:pk>/study/', views.word_list_study, name='word_list_study'),
    path('lists/<int:pk>/export/', views.word_list_export, name='word_list_export'),
    path('lists/<int:pk>/remove/<int:word_id>/', views.word_list_remove_word, name='word_list_remove_word'),
    path('word/<int:pk>/notes/', views.save_word_note, name='save_word_note'),
    path('<slug:slug>/', views.category_detail, name='category_detail'),
    path('<slug:slug>/study/', views.study_category, name='study_category'),
]
