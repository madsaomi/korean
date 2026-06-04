from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserLessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey('lessons.Lesson', on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'lesson']
        verbose_name_plural = 'User lesson progress'

    def __str__(self):
        return f'{self.user.username} — {self.lesson.title} ({self.score}%)'

class UserWordProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='word_progress')
    word = models.ForeignKey('vocabulary.Word', on_delete=models.CASCADE)
    learned = models.BooleanField(default=False)
    review_count = models.IntegerField(default=0)
    next_review = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, default='')
    learned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'word']

    def __str__(self):
        return f'{self.user.username} — {self.word.korean}'

class UserQuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_results')
    quiz = models.ForeignKey('quiz.Quiz', on_delete=models.CASCADE)
    score = models.IntegerField()
    total = models.IntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)

    def percentage(self):
        return int((self.score / self.total) * 100) if self.total else 0

    class Meta:
        ordering = ['-completed_at']
