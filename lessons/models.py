from django.db import models

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    level = models.CharField(max_length=20, choices=[
        ('beginner', 'С нуля'),
        ('elementary', 'Начальный'),
        ('intermediate', 'Средний'),
    ], default='beginner')
    order = models.IntegerField(default=0)
    image = models.ImageField(upload_to='courses/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.course.title} — {self.title}'

class LessonStep(models.Model):
    STEP_TYPES = [
        ('text', 'Текст'),
        ('image', 'Изображение'),
        ('quiz', 'Тест'),
    ]
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='steps')
    step_type = models.CharField(max_length=10, choices=STEP_TYPES, default='text')
    title = models.CharField(max_length=200, blank=True)
    content_korean = models.TextField(blank=True)
    content_russian = models.TextField(blank=True)
    image = models.ImageField(upload_to='steps/', blank=True, null=True)
    audio_url = models.CharField(max_length=500, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'Step {self.order}: {self.title or self.lesson.title}'
