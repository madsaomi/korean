from django.contrib import admin
from .models import LibraryPage, ReadingProgress, Bookmark, Note, Highlight, LibraryTag


@admin.register(LibraryPage)
class LibraryPageAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'word_count', 'read_time']
    search_fields = ['name', 'content']
    ordering = ['order']


@admin.register(ReadingProgress)
class ReadingProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'slug', 'read', 'read_at']
    list_filter = ['read']
    search_fields = ['user__username', 'slug']
    date_hierarchy = 'read_at'


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'slug', 'created_at']
    search_fields = ['user__username', 'title', 'slug']
    date_hierarchy = 'created_at'


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'slug', 'anchor', 'created_at']
    search_fields = ['user__username', 'slug', 'content']
    date_hierarchy = 'created_at'


@admin.register(LibraryTag)
class LibraryTagAdmin(admin.ModelAdmin):
    list_display = ['user', 'slug', 'tag']
    list_filter = ['tag']
    search_fields = ['user__username', 'slug', 'tag']


@admin.register(Highlight)
class HighlightAdmin(admin.ModelAdmin):
    list_display = ['user', 'slug', 'color', 'text', 'created_at']
    list_filter = ['color']
    search_fields = ['user__username', 'slug', 'text']
