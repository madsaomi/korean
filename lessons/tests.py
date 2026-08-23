import pytest
from django.contrib.auth.models import User

from lessons.models import Course, Lesson, LessonStep


@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='testpass123')


@pytest.fixture
def course():
    return Course.objects.create(
        title='Базовый курс', description='Основы корейского', level='beginner', order=1
    )


@pytest.fixture
def lesson(course):
    return Lesson.objects.create(course=course, title='Урок 1', order=1)


@pytest.mark.django_db
class TestLessonModels:
    def test_course_defaults(self, course):
        assert course.level == 'beginner'
        assert 'Базовый курс' in str(course)

    def test_lesson_belongs_to_course(self, course, lesson):
        assert lesson.course == course
        assert course.lessons.count() == 1

    def test_lesson_ordering(self, course, lesson):
        second = Lesson.objects.create(course=course, title='Урок 2', order=2)
        first = Lesson.objects.get(course=course, order=1)
        assert list(course.lessons.all()) == [first, second]

    def test_step_types(self, course, lesson):
        step = LessonStep.objects.create(
            lesson=lesson, step_type='quiz', title='Мини-тест', order=1
        )
        assert step.step_type == 'quiz'
        assert lesson.steps.count() == 1


@pytest.mark.django_db
class TestLessonViews:
    def test_lesson_list_public(self, client, course):
        resp = client.get('/lessons/')
        assert resp.status_code == 200

    def test_lesson_detail_requires_login(self, client, course, lesson):
        resp = client.get(f'/lessons/{course.id}/{lesson.id}/')
        assert resp.status_code == 302

    def test_lesson_detail_authenticated(self, client, user, course, lesson):
        client.force_login(user)
        resp = client.get(f'/lessons/{course.id}/{lesson.id}/')
        assert resp.status_code == 200
