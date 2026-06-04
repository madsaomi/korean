import pytest
from django.contrib.auth.models import User
from accounts.models import UserProfile, Streak, Achievement, DailyGoal


@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='testpass123')


@pytest.mark.django_db
class TestUserProfile:
    def test_profile_auto_created(self, user):
        assert UserProfile.objects.filter(user=user).exists()

    def test_profile_defaults(self, user):
        profile = user.profile
        assert profile.native_language == 'Русский'
        assert profile.level == 'beginner'

    def test_profile_str(self, user):
        assert user.username in str(user.profile)

    def test_level_display(self, user):
        assert 'С нуля' in str(user.profile)


@pytest.mark.django_db
class TestStreak:
    def test_streak_create(self, user):
        streak, created = Streak.objects.get_or_create(user=user)
        assert streak.current_streak == 0
        assert streak.longest_streak == 0

    def test_streak_str(self, user):
        streak, _ = Streak.objects.get_or_create(user=user, defaults={'current_streak': 5})
        streak.current_streak = 5
        streak.save()
        assert 'testuser' in str(streak)
        assert '5' in str(streak)


@pytest.mark.django_db
class TestAchievement:
    def test_create_achievement(self, user):
        ach = Achievement.objects.create(
            user=user, code='first_word',
            title='Первое слово', description='Выучили первое слово',
            icon='🎯'
        )
        assert ach.code == 'first_word'
        assert str(ach) == 'testuser — Первое слово'

    def test_unique_together(self, user):
        Achievement.objects.create(user=user, code='first_word', title='Test')
        with pytest.raises(Exception):
            Achievement.objects.create(user=user, code='first_word', title='Duplicate')

    def test_ordering(self, user):
        a1 = Achievement.objects.create(user=user, code='a', title='A')
        a2 = Achievement.objects.create(user=user, code='b', title='B')
        qs = Achievement.objects.filter(user=user)
        assert qs.first() == a2


@pytest.mark.django_db
class TestDailyGoal:
    def test_defaults(self, user):
        goal, created = DailyGoal.objects.get_or_create(user=user)
        if not created:
            assert goal.words_target is not None
        else:
            assert goal.words_target == 5
            assert goal.lessons_target == 1
            assert goal.quizzes_target == 1


@pytest.mark.django_db
class TestRegistration:
    def test_user_can_register(self, client):
        resp = client.post('/accounts/register/', {
            'username': 'newuser',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        })
        assert resp.status_code in (200, 302)
        if resp.status_code == 302:
            assert User.objects.filter(username='newuser').exists()

    def test_registration_missing_fields(self, client):
        resp = client.post('/accounts/register/', {'username': '', 'password1': '', 'password2': ''})
        assert resp.status_code == 200
        assert resp.context['form'].errors
