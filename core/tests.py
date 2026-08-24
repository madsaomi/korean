from datetime import timedelta

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from accounts.models import Streak
from core.middleware import StreakMiddleware


@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='testpass123')


def _visit(rf, user):
    from django.contrib.messages.storage.fallback import FallbackStorage
    from django.http import HttpResponse

    req = rf.get('/')
    req.user = user
    req.session = {}
    req._messages = FallbackStorage(req)
    mw = StreakMiddleware(lambda r: HttpResponse('ok'))
    return mw(req)


def _streak_for(user, *, current, last_days_ago, freezes=1):
    # post_save signal already created a Streak for the user
    s, _ = Streak.objects.update_or_create(
        user=user,
        defaults={
            'current_streak': current,
            'longest_streak': current,
            'last_active_date': timezone.localdate() - timedelta(days=last_days_ago),
            'freezes': freezes,
        },
    )
    return s


@pytest.mark.django_db
class TestStreakMiddleware:
    def test_middleware_updates_streak(self, rf, user):
        resp = _visit(rf, user)
        assert resp.status_code == 200

    def test_streak_created_on_first_visit(self, rf, user):
        _visit(rf, user)
        assert Streak.objects.filter(user=user).exists()

    def test_consecutive_day_increments(self, rf, user):
        s = _streak_for(user, current=4, last_days_ago=1)
        _visit(rf, user)
        s.refresh_from_db()
        assert s.current_streak == 5
        assert s.freezes == 1

    def test_gap_resets_without_freeze(self, rf, user):
        s = _streak_for(user, current=9, last_days_ago=2, freezes=0)
        _visit(rf, user)
        s.refresh_from_db()
        assert s.current_streak == 1
        assert s.freezes == 0

    def test_freeze_bridges_one_missed_day(self, rf, user):
        s = _streak_for(user, current=6, last_days_ago=2, freezes=1)
        _visit(rf, user)
        s.refresh_from_db()
        assert s.current_streak == 7
        # Freeze was consumed (-1) but hitting 7 days granted a new one (+1)
        assert s.freezes == 1

    def test_no_freeze_rescue_after_two_missed_days(self, rf, user):
        s = _streak_for(user, current=10, last_days_ago=3, freezes=2)
        _visit(rf, user)
        s.refresh_from_db()
        assert s.current_streak == 1
        assert s.freezes == 2

    def test_seven_day_milestone_grants_freeze(self, rf, user):
        s = _streak_for(user, current=6, last_days_ago=1, freezes=1)
        _visit(rf, user)
        s.refresh_from_db()
        assert s.current_streak == 7
        assert s.freezes == 2

    def test_freeze_cap_at_max(self, rf, user):
        s = _streak_for(user, current=13, last_days_ago=1, freezes=3)
        _visit(rf, user)
        s.refresh_from_db()
        assert s.current_streak == 14
        assert s.freezes == Streak.MAX_FREEZES

    def test_same_day_revisit_does_not_double_count(self, rf, user):
        s = _streak_for(user, current=5, last_days_ago=0)
        _visit(rf, user)
        _visit(rf, user)
        s.refresh_from_db()
        assert s.current_streak == 5


@pytest.mark.django_db
class TestCoreViews:
    def test_homepage(self, client):
        resp = client.get('/')
        assert resp.status_code == 200

    def test_leaderboard(self, client):
        resp = client.get('/leaderboard/')
        assert resp.status_code in (200, 302)

    def test_search_page(self, client):
        resp = client.get('/search/')
        assert resp.status_code == 200
