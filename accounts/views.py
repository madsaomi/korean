from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
import json
from accounts.models import UserProfile, Streak
from progress.models import UserLessonProgress, UserQuizResult, UserWordProgress
from vocabulary.models import Word
from lessons.models import Lesson

class SignUpForm(UserCreationForm):
    native_language = forms.CharField(max_length=50, initial='Русский', label='Родной язык')
    level = forms.ChoiceField(choices=UserProfile.LEVELS, initial='beginner', label='Уровень')

    class Meta:
        model = User
        fields = ('username', 'native_language', 'level', 'password1', 'password2')

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
    streak = getattr(request.user, 'streak', None)
    if not streak:
        streak = Streak.objects.create(user=request.user)
    lessons_done = UserLessonProgress.objects.filter(user=request.user, completed=True).count()
    quizzes_done = UserQuizResult.objects.filter(user=request.user).count()
    words_learned = UserWordProgress.objects.filter(user=request.user, learned=True).count()
    quiz_history = UserQuizResult.objects.filter(user=request.user)[:10]
    words_in_review = UserWordProgress.objects.filter(
        user=request.user, learned=False
    ).exclude(next_review=None).count()

    now = timezone.now()
    last_14 = [now.date() - timedelta(days=i) for i in range(13, -1, -1)]
    quiz_chart = []
    for d in last_14:
        results = UserQuizResult.objects.filter(
            user=request.user, completed_at__date=d
        )
        avg = sum(r.percentage() for r in results) / results.count() if results else None
        quiz_chart.append({'date': d.isoformat()[5:], 'avg': avg})

    total_lessons = Lesson.objects.count()
    achievements_count = request.user.achievements.count()
    total_possible = 11

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
    return render(request, 'accounts/achievements.html', {'achievements': achievements})

@login_required
def daily_goals_page(request):
    from accounts.models import DailyGoal
    goal, _ = DailyGoal.objects.get_or_create(user=request.user)
    from django.utils import timezone
    from datetime import timedelta
    from progress.models import UserLessonProgress, UserQuizResult, UserWordProgress

    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)

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
        goal.words_target = max(1, int(request.POST.get('words_target', 5)))
        goal.lessons_target = max(1, int(request.POST.get('lessons_target', 1)))
        goal.quizzes_target = max(1, int(request.POST.get('quizzes_target', 1)))
        goal.save(update_fields=['words_target', 'lessons_target', 'quizzes_target'])
        messages.success(request, '✅ Цели обновлены')
        return redirect('daily_goals')

    return render(request, 'accounts/daily_goals.html', {
        'goal': goal,
        'lessons_today': lessons_today,
        'quizzes_today': quizzes_today,
        'words_today': words_today,
    })
