from datetime import timedelta

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from progress.models import UserQuizResult
from quiz.models import Answer, Question, Quiz

SESSION_START_PREFIX = 'quiz_started_'


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
        UserQuizResult.objects.create(user=user, quiz=quiz, score=5, total=10)
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


@pytest.mark.django_db
class TestQuizServerTimer:
    def _correct_answer(self, question):
        return question.answers.get(is_correct=True)

    def test_submit_without_start_rejected(self, client, user, quiz):
        client.force_login(user)
        resp = client.post(f'/quiz/{quiz.id}/submit/', {})
        assert resp.status_code == 302
        assert UserQuizResult.objects.filter(user=user).count() == 0

    def test_submit_after_visit_accepted(self, client, user, quiz):
        client.force_login(user)
        client.get(f'/quiz/{quiz.id}/')
        first = quiz.questions.order_by('id').first()
        resp = client.post(
            f'/quiz/{quiz.id}/submit/',
            {f'q_{first.id}': str(self._correct_answer(first).id)},
        )
        assert resp.status_code == 200
        result = UserQuizResult.objects.get(user=user)
        assert result.score == 1
        assert result.total == 2

    def test_expired_attempt_rejected(self, client, user, quiz):
        client.force_login(user)
        client.get(f'/quiz/{quiz.id}/')

        session = client.session
        session[SESSION_START_PREFIX + str(quiz.pk)] = (
            timezone.now() - timedelta(hours=2)
        ).isoformat()
        session.save()

        resp = client.post(f'/quiz/{quiz.id}/submit/', {})
        assert resp.status_code == 302
        assert UserQuizResult.objects.filter(user=user).count() == 0

    def test_no_limit_quiz_needs_no_start(self, client, user):
        quiz = Quiz.objects.create(title='Без лимита', time_limit=0)
        q = Question.objects.create(quiz=quiz, question_russian='Q?')
        Answer.objects.create(question=q, text='да', is_correct=True)

        client.force_login(user)
        resp = client.post(f'/quiz/{quiz.id}/submit/', {f'q_{q.id}': 'да'})
        assert resp.status_code == 200
        assert UserQuizResult.objects.get(user=user).score == 1


@pytest.mark.django_db
class TestWritingAnswers:
    def test_numeric_writing_answer_compared_as_text(self, client, user):
        quiz = Quiz.objects.create(title='Writing', time_limit=0)
        q = Question.objects.create(
            quiz=quiz, question_type='writing', question_russian='Сколько?'
        )
        Answer.objects.create(question=q, text='4', is_correct=True)

        client.force_login(user)
        client.get(f'/quiz/{quiz.id}/')
        resp = client.post(f'/quiz/{quiz.id}/submit/', {f'q_{q.id}': '4'})

        assert resp.status_code == 200
        assert UserQuizResult.objects.get(user=user).score == 1

    def test_text_answer_case_and_spaces_normalized(self, client, user):
        quiz = Quiz.objects.create(title='Text', time_limit=0)
        q = Question.objects.create(
            quiz=quiz, question_type='writing', question_russian='Перевод'
        )
        Answer.objects.create(question=q, text='рис', is_correct=True)

        client.force_login(user)
        client.get(f'/quiz/{quiz.id}/')
        resp = client.post(f'/quiz/{quiz.id}/submit/', {f'q_{q.id}': '  РИС '})

        assert resp.status_code == 200
        assert UserQuizResult.objects.get(user=user).score == 1
