from django.contrib import admin
from .models import UserLessonProgress, UserWordProgress, UserQuizResult

admin.site.register(UserLessonProgress)
admin.site.register(UserWordProgress)
admin.site.register(UserQuizResult)
