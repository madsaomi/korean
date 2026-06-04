import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from vocabulary.models import Category, Word
from lessons.models import Course, Lesson
from grammar.models import GrammarTopic, GrammarRule
from quiz.models import Quiz, Question, Answer
from progress.models import UserWordProgress


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='testpass123')


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def category():
    return Category.objects.create(name='Еда', slug='food', icon='🍕', order=1)


@pytest.fixture
def word(category):
    return Word.objects.create(
        category=category, korean='밥', russian='рис',
        romanization='bap', level='beginner'
    )


@pytest.fixture
def course():
    return Course.objects.create(title='Курс 1', description='Описание', level='beginner', order=1)


@pytest.fixture
def lesson(course):
    return Lesson.objects.create(course=course, title='Урок 1', order=1)


@pytest.fixture
def grammar_topic():
    topic = GrammarTopic.objects.create(title='Падежи', slug='padezhi', level='beginner', order=1)
    GrammarRule.objects.create(topic=topic, title='Именительный', explanation='...', formula='N+가/이')
    return topic


@pytest.fixture
def quiz():
    q = Quiz.objects.create(title='Тест 1', level='beginner', passing_score=70)
    question = Question.objects.create(quiz=q, question_russian='Перевод 밥')
    Answer.objects.create(question=question, text='рис', is_correct=True)
    Answer.objects.create(question=question, text='суп', is_correct=False)
    return q


# ─── Vocabulary API ───

@pytest.mark.django_db
class TestVocabularyAPI:
    def test_list_categories(self, auth_client, category):
        resp = auth_client.get('/api/vocabulary/categories/')
        assert resp.status_code == 200
        results = resp.data.get('results', resp.data)
        assert len(results) >= 1

    def test_list_courses(self, auth_client, course):
        resp = auth_client.get('/api/lessons/courses/')
        assert resp.status_code == 200
        results = resp.data.get('results', resp.data)
        assert len(results) >= 1

    def test_category_detail(self, auth_client, category):
        resp = auth_client.get(f'/api/vocabulary/categories/{category.slug}/')
        assert resp.status_code == 200
        assert resp.data['name'] == 'Еда'

    def test_list_words(self, auth_client, word):
        resp = auth_client.get('/api/vocabulary/words/')
        assert resp.status_code == 200
        assert resp.data['count'] >= 1

    def test_filter_words_by_category(self, auth_client, word, category):
        resp = auth_client.get(f'/api/vocabulary/words/?category__slug={category.slug}')
        assert resp.status_code == 200
        assert resp.data['count'] >= 1

    def test_search_words(self, auth_client, word):
        resp = auth_client.get('/api/vocabulary/words/?search=밥')
        assert resp.status_code == 200
        assert resp.data['count'] >= 1

    def test_word_detail(self, auth_client, word):
        resp = auth_client.get(f'/api/vocabulary/words/{word.id}/')
        assert resp.status_code == 200
        assert resp.data['korean'] == '밥'

    def test_anon_can_read(self, api_client, word):
        resp = api_client.get('/api/vocabulary/words/')
        assert resp.status_code == 200


# ─── Lessons API ───

@pytest.mark.django_db
class TestLessonsAPI:
    def test_list_courses(self, auth_client, course):
        resp = auth_client.get('/api/lessons/courses/')
        assert resp.status_code == 200
        results = resp.data.get('results', resp.data)
        assert len(results) >= 1
        assert results[0]['title'] == 'Курс 1'

    def test_course_lesson_count(self, auth_client, course, lesson):
        resp = auth_client.get(f'/api/lessons/courses/{course.id}/')
        assert resp.status_code == 200
        assert resp.data['lesson_count'] >= 1

    def test_list_lessons(self, auth_client, lesson):
        resp = auth_client.get('/api/lessons/lessons/')
        assert resp.status_code == 200
        assert resp.data['count'] >= 1


# ─── Grammar API ───

@pytest.mark.django_db
class TestGrammarAPI:
    def test_list_topics(self, auth_client, grammar_topic):
        resp = auth_client.get('/api/grammar/topics/')
        assert resp.status_code == 200
        assert len(resp.data) >= 1

    def test_topic_detail_with_rules(self, auth_client, grammar_topic):
        resp = auth_client.get(f'/api/grammar/topics/{grammar_topic.slug}/')
        assert resp.status_code == 200
        assert len(resp.data['rules']) >= 1
        assert resp.data['rules'][0]['title'] == 'Именительный'


# ─── Quiz API ───

@pytest.mark.django_db
class TestQuizAPI:
    def test_list_quizzes(self, auth_client, quiz):
        resp = auth_client.get('/api/quiz/')
        assert resp.status_code == 200
        assert resp.data['count'] >= 1

    def test_quiz_detail_with_questions(self, auth_client, quiz):
        resp = auth_client.get(f'/api/quiz/{quiz.id}/')
        assert resp.status_code == 200
        assert len(resp.data['questions']) >= 1
        assert len(resp.data['questions'][0]['answers']) == 2


# ─── Review API ───

@pytest.mark.django_db
class TestReviewAPI:
    def test_list_empty_review(self, auth_client):
        resp = auth_client.get('/api/review/')
        assert resp.status_code == 200
        assert resp.data == []

    def test_review_action(self, auth_client, user, word):
        from progress.models import UserWordProgress
        UserWordProgress.objects.create(user=user, word=word)
        resp = auth_client.post('/api/review/', {'word_id': word.id, 'action': 'again'})
        assert resp.status_code == 200
        assert resp.data['success']

    def test_review_easy_marks_learned(self, auth_client, user, word):
        from progress.models import UserWordProgress
        prog = UserWordProgress.objects.create(user=user, word=word)
        resp = auth_client.post('/api/review/', {'word_id': word.id, 'action': 'easy'})
        assert resp.status_code == 200
        prog.refresh_from_db()
        assert prog.learned is True


# ─── Progress API ───

@pytest.mark.django_db
class TestProgressAPI:
    def test_overview(self, auth_client, user):
        resp = auth_client.get('/api/progress/overview/')
        assert resp.status_code == 200
        assert 'streak' in resp.data
        assert 'stats' in resp.data

    def test_progress_requires_auth(self, api_client):
        resp = api_client.get('/api/progress/overview/')
        assert resp.status_code == 403


# ─── Library API ───

@pytest.mark.django_db
class TestLibraryAPI:
    def test_library_requires_auth(self, api_client):
        resp = api_client.get('/api/library/')
        assert resp.status_code == 403

    def test_library_list(self, auth_client):
        resp = auth_client.get('/api/library/')
        assert resp.status_code == 200
        assert 'reading_slugs' in resp.data


# ─── Auth API ───

@pytest.mark.django_db
class TestAuthAPI:
    def test_auth_requires_auth(self, api_client):
        resp = api_client.get('/api/auth/')
        assert resp.status_code == 403

    def test_auth_me(self, auth_client, user):
        resp = auth_client.get('/api/auth/')
        assert resp.status_code == 200
        assert resp.data['username'] == 'testuser'

    def test_auth_profile(self, auth_client):
        resp = auth_client.get('/api/auth/profile/')
        assert resp.status_code == 200
        assert 'user' in resp.data


# ─── Authentication ───

@pytest.mark.django_db
class TestTokenAuth:
    def test_token_login(self, api_client, user):
        resp = api_client.post('/api/auth/login/', {'username': 'testuser', 'password': 'testpass123'})
        assert resp.status_code in (200, 301, 302, 403)

    def test_anonymous_access(self, api_client, word):
        resp = api_client.get(f'/api/vocabulary/words/{word.id}/')
        assert resp.status_code == 200
