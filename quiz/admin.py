from django.contrib import admin

from .models import Answer, Question, Quiz


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 2

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ['title', 'level', 'passing_score', 'order']
    list_editable = ['order']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]
    list_display = ['question_russian', 'quiz', 'question_type', 'order']

admin.site.register(Answer)
