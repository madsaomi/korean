from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'vocabulary/categories', views.CategoryViewSet, basename='api-category')
router.register(r'vocabulary/words', views.WordViewSet, basename='api-word')
router.register(r'lessons/courses', views.CourseViewSet, basename='api-course')
router.register(r'lessons/lessons', views.LessonViewSet, basename='api-lesson')
router.register(r'grammar/topics', views.GrammarTopicViewSet, basename='api-grammar-topic')
router.register(r'grammar/exercises', views.GrammarExerciseViewSet, basename='api-grammar-exercise')
router.register(r'quiz', views.QuizViewSet, basename='api-quiz')
router.register(r'progress', views.ProgressViewSet, basename='api-progress')
router.register(r'review', views.ReviewViewSet, basename='api-review')
router.register(r'library', views.LibraryViewSet, basename='api-library')
router.register(r'auth', views.AuthViewSet, basename='api-auth')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]
