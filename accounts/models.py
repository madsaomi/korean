from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


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
    MAX_FREEZES = 3

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='streak')
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True, default=None)
    freezes = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.user.username} — {self.current_streak} дней'

class Achievement(models.Model):
    # Single source of truth for all achievements: code -> (icon, title, description)
    CATALOG = {
        'streak_3': ('🔥', '3 дня подряд', 'Три дня занятий без перерыва!'),
        'streak_7': ('🔥🔥', 'Неделя без пропусков', 'Целая неделя ежедневных занятий!'),
        'streak_30': ('💪', 'Месяц силы', '30 дней подряд — ты легенда!'),
        'first_lesson': ('📚', 'Первый урок', 'Пройди свой первый урок'),
        'five_lessons': ('📚📚', '5 уроков', 'Пройди 5 уроков'),
        'ten_lessons': ('📚📚📚', '10 уроков', 'Пройди 10 уроков — серьёзный подход!'),
        'first_quiz': ('🎯', 'Первый тест', 'Пройди свой первый тест'),
        'five_quizzes': ('🎯🎯', '5 тестов', 'Пройди 5 тестов'),
        'ten_words': ('📖', '10 слов', 'Выучи 10 слов'),
        'fifty_words': ('📖📖', '50 слов', 'Выучи 50 слов'),
        'hundred_words': ('💯', '100 слов', 'Выучи 100 слов — отлично!'),
    }
    ALL_CODES = frozenset(CATALOG)

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
