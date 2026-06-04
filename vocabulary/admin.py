from django.contrib import admin
from .models import Category, Word, WordList

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['name']}
    list_display = ['name', 'order']
    list_editable = ['order']

@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ['korean', 'russian', 'category', 'level']
    list_filter = ['category', 'level']
    search_fields = ['korean', 'russian']

admin.site.register(WordList)
