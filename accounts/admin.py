from django.contrib import admin
from .models import UserProfile, Streak, Achievement, DailyGoal

admin.site.register(UserProfile)
admin.site.register(Streak)
admin.site.register(Achievement)
admin.site.register(DailyGoal)
