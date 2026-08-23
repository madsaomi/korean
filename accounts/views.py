import json
from datetime import timedelta

from django import forms
from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.shortcuts import redirect, render
from django.utils import timezone

from accounts.models import Achievement, DailyGoal, Streak, UserProfile
from lessons.models import Lesson
from progress.models import UserLessonProgress, UserQuizResult, UserWordProgress


class SignUpForm(UserCreationForm):
    native_language = forms.CharField(max_length=50, initial='Русский', label='Родной язык')
    level = forms.ChoiceField(choices=UserProfile.LEVELS, initial='beginner', label='Уровень')

    class Meta:
        model = User
        fields = ('username',)

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            profile = user.profile
            profile.native_language = self.cleaned_data['native_language']
            profile.level = self.cleaned_data['level']
            profile.save(update_fields=['native_language', 'level'])
        return user

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('native_language', 'level')

def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    profile = request.user.profile
    streak, _ = Streak.objects.get_or_create(user=request.user)
    lessons_done = UserLessonProgress.objects.filter(user=request.user, completed=True).count()
    quizzes_done = UserQuizResult.objects.filter(user=request.user).count()
    words_learned = UserWordProgress.objects.filter(user=request.user, learned=True).count()
    quiz_history = UserQuizResult.objects.filter(user=request.user)[:10]
    words_in_review = UserWordProgress.objects.filter(
        user=request.user, next_review__lte=timezone.now()
    ).count()

    last_14 = [timezone.localdate() - timedelta(days=i) for i in range(13, -1, -1)]
    agg = (
        UserQuizResult.objects
        .filter(user=request.user, completed_at__date__gte=last_14[0])
        .annotate(day=TruncDate('completed_at'))
        .values('day')
        .annotate(total_score=Sum('score'), total_total=Sum('total'))
    )
    avg_by_day = {
        row['day']: int((row['total_score'] / row['total_total']) * 100)
        if row['total_total'] else None
        for row in agg
    }
    quiz_chart = []
    for d in last_14:
        quiz_chart.append({'date': d.isoformat()[5:], 'avg': avg_by_day.get(d)})

    total_lessons = Lesson.objects.count()
    achievements_count = request.user.achievements.count()
    total_possible = len(Achievement.ALL_CODES)

    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'streak': streak,
        'lessons_done': lessons_done,
        'quizzes_done': quizzes_done,
        'words_learned': words_learned,
        'quiz_history': quiz_history,
        'words_in_review': words_in_review,
        'quiz_chart_json': json.dumps(quiz_chart),
        'achievements_count': achievements_count,
        'total_possible': total_possible,
        'total_lessons': total_lessons,
    })

@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Профиль обновлён')
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=profile)
    return render(request, 'accounts/edit_profile.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, '✅ Пароль изменён')
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})

@login_required
def achievements_page(request):
    achievements = request.user.achievements.all()
    earned_codes = set(achievements.values_list('code', flat=True))
    all_achievements = [
        {'code': code, 'icon': icon, 'title': title}
        for code, (icon, title, _description) in Achievement.CATALOG.items()
    ]
    return render(request, 'accounts/achievements.html', {
        'achievements': achievements,
        'all_achievements': all_achievements,
        'earned_codes': earned_codes,
    })

@login_required
def daily_goals_page(request):
    goal, _ = DailyGoal.objects.get_or_create(user=request.user)

    today = timezone.localdate()

    lessons_today = UserLessonProgress.objects.filter(
        user=request.user, completed_at__date=today
    ).count()
    quizzes_today = UserQuizResult.objects.filter(
        user=request.user, completed_at__date=today
    ).count()
    words_today = UserWordProgress.objects.filter(
        user=request.user, learned=True, learned_at__date=today
    ).count()

    if request.method == 'POST':
        try:
            goal.words_target = max(1, min(100, int(request.POST.get('words_target', 5))))
            goal.lessons_target = max(1, min(50, int(request.POST.get('lessons_target', 1))))
            goal.quizzes_target = max(1, min(50, int(request.POST.get('quizzes_target', 1))))
        except (ValueError, TypeError):
            messages.error(request, '❌ Введите корректные числа')
            return redirect('daily_goals')
        goal.save(update_fields=['words_target', 'lessons_target', 'quizzes_target'])
        messages.success(request, '✅ Цели обновлены')
        return redirect('daily_goals')

    return render(request, 'accounts/daily_goals.html', {
        'goal': goal,
        'lessons_today': lessons_today,
        'quizzes_today': quizzes_today,
        'words_today': words_today,
    })
