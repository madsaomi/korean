from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, default='📚')
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order']

    def __str__(self):
        return self.name

class Word(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='words')
    korean = models.CharField(max_length=200)
    russian = models.CharField(max_length=200)
    romanization = models.CharField(max_length=200, blank=True)
    example_sentence = models.TextField(blank=True)
    example_translation = models.TextField(blank=True)
    audio_url = models.CharField(max_length=500, blank=True)
    level = models.CharField(max_length=20, choices=[
        ('beginner', 'A1'),
        ('elementary', 'A2'),
        ('intermediate', 'B1'),
    ], default='beginner')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.korean} — {self.russian}'

class WordList(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='word_lists')
    name = models.CharField(max_length=200)
    words = models.ManyToManyField(Word, related_name='word_lists')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} ({self.user.username})'
