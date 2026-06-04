import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from progress.models import UserLessonProgress, UserWordProgress, UserQuizResult
from vocabulary.models import Category, Word
from lessons.models import Course, Lesson
from quiz.models import Quiz


@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='testpass123')


@pytest.fixture
def word():
    cat = Category.objects.create(name='Еда', slug='food')
    return Word.objects.create(category=cat, korean='밥', russian='рис')


@pytest.fixture
def lesson():
    course = Course.objects.create(title='Курс 1', level='beginner')
    return Lesson.objects.create(course=course, title='Урок 1', order=1)


@pytest.fixture
def quiz():
    return Quiz.objects.create(title='Test Quiz')


@pytest.mark.django_db
class TestUserLessonProgress:
    def test_create(self, user, lesson):
        lp = UserLessonProgress.objects.create(user=user, lesson=lesson, completed=True, score=85)
        assert lp.completed is True
        assert lp.score == 85
        assert str(lp) == 'testuser — Урок 1 (85%)'

    def test_unique_together(self, user, lesson):
        UserLessonProgress.objects.create(user=user, lesson=lesson)
        with pytest.raises(Exception):
            UserLessonProgress.objects.create(user=user, lesson=lesson)


@pytest.mark.django_db
class TestUserWordProgress:
    def test_create(self, user, word):
        wp = UserWordProgress.objects.create(user=user, word=word, learned=True)
        assert wp.learned is True
        assert wp.review_count == 0
        assert str(wp) == 'testuser — 밥'

    def test_next_review_default(self, user, word):
        wp = UserWordProgress.objects.create(user=user, word=word)
        assert wp.next_review <= timezone.now()

    def test_unique_together(self, user, word):
        UserWordProgress.objects.create(user=user, word=word)
        with pytest.raises(Exception):
            UserWordProgress.objects.create(user=user, word=word)


@pytest.mark.django_db
class TestUserQuizResult:
    def test_create(self, user, quiz):
        qr = UserQuizResult.objects.create(user=user, score=8, total=10, quiz=quiz)
        assert qr.percentage() == 80

    def test_percentage_zero_total(self, user, quiz):
        qr = UserQuizResult.objects.create(user=user, score=0, total=0, quiz=quiz)
        assert qr.percentage() == 0
