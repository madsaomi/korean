from django.contrib import admin
from .models import GrammarTopic, GrammarRule, GrammarExercise

class GrammarRuleInline(admin.TabularInline):
    model = GrammarRule
    extra = 1

@admin.register(GrammarTopic)
class GrammarTopicAdmin(admin.ModelAdmin):
    inlines = [GrammarRuleInline]
    prepopulated_fields = {'slug': ['title']}
    list_display = ['title', 'level', 'order']
    list_editable = ['order']

admin.site.register(GrammarRule)

@admin.register(GrammarExercise)
class GrammarExerciseAdmin(admin.ModelAdmin):
    list_display = ['question', 'difficulty', 'order']
    list_filter = ['difficulty', 'topic']
    list_editable = ['order']
