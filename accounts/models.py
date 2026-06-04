from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class UserProfile(models.Model):
    LEVELS = [
        ('beginner', 'С нуля'),
        ('elementary', 'Начальный'),
        ('intermediate', 'Средний'),
        ('upper_intermediate', 'Выше среднего'),
        ('advanced', 'Продвинутый'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    native_language = models.CharField(max_length=50, default='Русский')
    level = models.CharField(max_length=20, choices=LEVELS, default='beginner')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} ({self.get_level_display()})'

class Streak(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='streak')
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_active_date = models.DateField(default=timezone.now)

class Achievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    code = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, default='🏆')
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'code']
        ordering = ['-earned_at']

    def __str__(self):
        return f'{self.user.username} — {self.title}'

class DailyGoal(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='daily_goal')
    words_target = models.IntegerField(default=5)
    lessons_target = models.IntegerField(default=1)
    quizzes_target = models.IntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username}: {self.words_target}w/{self.lessons_target}l/{self.quizzes_target}q'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        Streak.objects.create(user=instance)
        DailyGoal.objects.create(user=instance)
