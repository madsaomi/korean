from django.contrib import admin
from .models import Course, Lesson, LessonStep

class LessonStepInline(admin.TabularInline):
    model = LessonStep
    extra = 1

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInline]
    list_display = ['title', 'level', 'order']
    list_editable = ['order']

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    inlines = [LessonStepInline]
    list_display = ['title', 'course', 'order']
    list_editable = ['order']
    list_filter = ['course']

admin.site.register(LessonStep)
