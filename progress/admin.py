from django.contrib import admin
from .models import UserLessonProgress, UserWordProgress, UserQuizResult


@admin.register(UserLessonProgress)
class UserLessonProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'completed', 'score', 'completed_at']
    list_filter = ['completed']
    search_fields = ['user__username', 'lesson__title']
    date_hierarchy = 'completed_at'
    raw_id_fields = ['user', 'lesson']


@admin.register(UserWordProgress)
class UserWordProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'word', 'learned', 'review_count', 'next_review', 'learned_at']
    list_filter = ['learned']
    search_fields = ['user__username', 'word__korean', 'word__russian']
    date_hierarchy = 'next_review'
    raw_id_fields = ['user', 'word']


@admin.register(UserQuizResult)
class UserQuizResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'score', 'total', 'percentage', 'completed_at']
    search_fields = ['user__username', 'quiz__title']
    date_hierarchy = 'completed_at'
    raw_id_fields = ['user', 'quiz']
