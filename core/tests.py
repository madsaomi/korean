import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from core.middleware import StreakMiddleware
from accounts.models import Streak


@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='testpass123')


@pytest.mark.django_db
class TestStreakMiddleware:
    def test_middleware_updates_streak(self, rf, user):
        req = rf.get('/')
        req.user = user
        req.session = {}
        from django.http import HttpResponse
        def get_response(req):
            return HttpResponse('ok')
        mw = StreakMiddleware(get_response)
        resp = mw(req)
        assert resp.status_code == 200

    def test_streak_created_on_first_visit(self, rf, user):
        req = rf.get('/')
        req.user = user
        req.session = {}
        from django.http import HttpResponse
        def get_response(req):
            return HttpResponse('ok')
        mw = StreakMiddleware(get_response)
        mw(req)
        assert Streak.objects.filter(user=user).exists()


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
