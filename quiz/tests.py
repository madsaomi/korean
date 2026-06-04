import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from quiz.models import Quiz, Question, Answer
from progress.models import UserQuizResult


@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='testpass123')


@pytest.fixture
def quiz():
    q = Quiz.objects.create(
        title='Тест хангыль', description='Проверка знаний',
        level='beginner', time_limit=300, passing_score=70
    )
    q1 = Question.objects.create(quiz=q, question_russian='Как читается ㄱ?')
    Answer.objects.create(question=q1, text='Г', is_correct=True)
    Answer.objects.create(question=q1, text='К', is_correct=False)
    Answer.objects.create(question=q1, text='Н', is_correct=False)

    q2 = Question.objects.create(quiz=q, question_russian='Как читается ㅏ?')
    Answer.objects.create(question=q2, text='А', is_correct=True)
    Answer.objects.create(question=q2, text='Я', is_correct=False)
    return q


@pytest.mark.django_db
class TestQuiz:
    def test_quiz_created(self, quiz):
        assert Quiz.objects.count() == 1
        assert quiz.questions.count() == 2

    def test_passing_score_default(self):
        q = Quiz.objects.create(title='Test')
        assert q.passing_score == 70


@pytest.mark.django_db
class TestQuestion:
    def test_question_answers(self, quiz):
        q = quiz.questions.first()
        assert q.answers.count() == 3
        correct = q.answers.filter(is_correct=True).first()
        assert correct is not None

    def test_correct_answer_first_question(self, quiz):
        q = quiz.questions.order_by('id').first()
        correct = q.answers.filter(is_correct=True).first()
        assert correct.text == 'Г'

    def test_correct_answer_second_question(self, quiz):
        q = quiz.questions.order_by('id').last()
        correct = q.answers.filter(is_correct=True).first()
        assert correct.text == 'А'


@pytest.mark.django_db
class TestUserQuizResult:
    def test_submit_result(self, user, quiz):
        result = UserQuizResult.objects.create(
            user=user, quiz=quiz, score=8, total=10
        )
        assert result.percentage() == 80

    def test_percentage_zero_division(self, user, quiz):
        result = UserQuizResult.objects.create(
            user=user, quiz=quiz, score=0, total=0
        )
        assert result.percentage() == 0

    def test_latest_first(self, user, quiz):
        r1 = UserQuizResult.objects.create(user=user, quiz=quiz, score=5, total=10)
        r2 = UserQuizResult.objects.create(user=user, quiz=quiz, score=9, total=10)
        qs = UserQuizResult.objects.filter(user=user)
        assert qs.first() == r2


@pytest.mark.django_db
class TestQuizViews:
    def test_quiz_list(self, client, quiz):
        resp = client.get('/quiz/')
        assert resp.status_code == 200

    def test_quiz_detail(self, client, quiz):
        resp = client.get(f'/quiz/{quiz.id}/')
        assert resp.status_code == 200

    def test_quiz_submit_requires_login(self, client, quiz):
        resp = client.post(f'/quiz/{quiz.id}/submit/', {'answers': '{}'})
        assert resp.status_code in (302, 403)
