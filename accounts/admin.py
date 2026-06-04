from django.contrib import admin
from .models import UserProfile, Streak, Achievement, DailyGoal


class AchievementInline(admin.TabularInline):
    model = Achievement
    extra = 0
    readonly_fields = ['code', 'title', 'earned_at']
    can_delete = False
    ordering = ['-earned_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'level', 'native_language', 'created_at']
    list_filter = ['level']
    search_fields = ['user__username', 'user__email']
    raw_id_fields = ['user']
    date_hierarchy = 'created_at'


@admin.register(Streak)
class StreakAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_streak', 'longest_streak', 'last_active_date']
    list_select_related = ['user']
    search_fields = ['user__username']
    date_hierarchy = 'last_active_date'


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'title', 'icon', 'earned_at']
    list_filter = ['code']
    search_fields = ['user__username', 'title', 'code']
    date_hierarchy = 'earned_at'


@admin.register(DailyGoal)
class DailyGoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'words_target', 'lessons_target', 'quizzes_target']
    search_fields = ['user__username']
