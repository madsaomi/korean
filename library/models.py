from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class LibraryPage(models.Model):
    slug = models.SlugField(max_length=200, unique=True)
    name = models.CharField(max_length=200)
    icon = models.CharField(max_length=10, default='📄')
    description = models.TextField(blank=True)
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)
    word_count = models.PositiveIntegerField(default=0)
    read_time = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Страница библиотеки'
        verbose_name_plural = 'Страницы библиотеки'

    def __str__(self):
        return self.name


class ReadingProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_progress')
    slug = models.CharField(max_length=200)
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'slug']
        verbose_name_plural = 'Reading progress'

    def __str__(self):
        return f'{self.user.username} — {self.slug} ({'✓' if self.read else '○'})'


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='library_bookmarks')
    slug = models.CharField(max_length=200)
    title = models.CharField(max_length=300)
    anchor = models.CharField(max_length=200, blank=True)
    note = models.TextField(blank=True)
    color = models.CharField(max_length=20, default='default')
    section = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} — {self.title}'


class Highlight(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='library_highlights')
    slug = models.CharField(max_length=200)
    anchor = models.CharField(max_length=200, blank=True)
    text = models.TextField()
    color = models.CharField(max_length=20, default='yellow')
    note = models.TextField(blank=True)
    start_offset = models.IntegerField(default=0)
    end_offset = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} — {self.text[:40]}'


class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='library_notes')
    slug = models.CharField(max_length=200)
    anchor = models.CharField(max_length=200, blank=True)
    highlighted_text = models.TextField(blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} — {self.highlighted_text[:50]}...'


class LibraryTag(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='library_tags')
    slug = models.CharField(max_length=200)
    tag = models.CharField(max_length=50)

    class Meta:
        unique_together = ['user', 'slug', 'tag']

    def __str__(self):
        return f'{self.user.username} — {self.slug}: {self.tag}'
