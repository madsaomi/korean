from django.db import models

class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    lesson = models.ForeignKey('lessons.Lesson', on_delete=models.SET_NULL, null=True, blank=True, related_name='quizzes')
    level = models.CharField(max_length=20, choices=[
        ('beginner', 'С нуля'),
        ('elementary', 'Начальный'),
        ('intermediate', 'Средний'),
    ], default='beginner')
    time_limit = models.IntegerField(default=0, help_text='Seconds (0 = no limit)')
    passing_score = models.IntegerField(default=70, help_text='Percentage to pass')
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Quizzes'
        ordering = ['order']

    def __str__(self):
        return self.title

class Question(models.Model):
    QUIZ_TYPES = [
        ('multiple_choice', 'Выбор ответа'),
        ('true_false', 'Правда / Ложь'),
        ('writing', 'Написание'),
    ]
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=20, choices=QUIZ_TYPES, default='multiple_choice')
    question_korean = models.TextField(blank=True)
    question_russian = models.TextField()
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.quiz.title} — Q{self.order}'

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    explanation = models.TextField(blank=True)

    def __str__(self):
        return f'{"✓" if self.is_correct else "✗"} {self.text}'

    class Meta:
        ordering = ['id']
