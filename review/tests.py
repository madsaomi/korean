from datetime import timedelta

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from progress.models import UserWordProgress
from review.services import (
    AGAIN_INTERVAL_MINUTES,
    InvalidReviewAction,
    WordNotDue,
    apply_review,
    pending_review_count,
)
from vocabulary.models import Category, Word


@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='testpass123')


@pytest.fixture
def word():
    category = Category.objects.create(name='Еда', slug='food')
    return Word.objects.create(
        category=category, korean='밥', russian='рис', level='beginner'
    )


@pytest.fixture
def prog(user, word):
    return UserWordProgress.objects.create(user=user, word=word)


@pytest.mark.django_db
class TestApplyReview:
    def test_again_resets_ladder(self, prog):
        prog.review_count = 4
        prog.next_review = timezone.now() - timezone.timedelta(minutes=1)
        prog.save()

        result = apply_review(prog.user, prog.word_id, 'again')

        assert result.review_count == 0
        delta = (result.next_review - timezone.now()).total_seconds()
        assert 0 < delta <= AGAIN_INTERVAL_MINUTES * 60 + 5

    def test_not_due_word_rejected(self, prog):
        prog.next_review = timezone.now() + timezone.timedelta(hours=1)
        prog.save()

        with pytest.raises(WordNotDue):
            apply_review(prog.user, prog.word_id, 'good')

    def test_good_advances_step_by_step(self, prog):
        apply_review(prog.user, prog.word_id, 'good')
        prog.refresh_from_db()
        assert prog.review_count == 1
        delta = (prog.next_review - timezone.now()).total_seconds()
        assert timedelta(days=1).total_seconds() - 60 < delta <= timedelta(days=1).total_seconds() + 60

    def test_good_caps_at_max_interval(self, prog):
        prog.review_count = 10
        prog.save()
        apply_review(prog.user, prog.word_id, 'good')
        prog.refresh_from_db()
        assert prog.review_count == 11
        delta = (prog.next_review - timezone.now()).total_seconds()
        assert abs(delta - 30 * 86400) <= 60

    def test_easy_marks_learned(self, prog):
        result = apply_review(prog.user, prog.word_id, 'easy')

        assert result.learned is True
        assert result.learned_at is not None
        assert result.review_count == 1
        delta = (result.next_review - timezone.now()).total_seconds()
        assert abs(delta - 7 * 86400) <= 60

    def test_easy_grants_achievement_at_threshold(self, user, word):
        extra_category = Category.objects.get(slug='food')
        UserWordProgress.objects.create(
            user=user,
            word=word,
            learned=True,
            learned_at=timezone.now(),
        )
        new_word = Word.objects.create(
            category=extra_category, korean='물', russian='вода'
        )
        UserWordProgress.objects.create(user=user, word=new_word)
        for i in range(9):
            filler = Word.objects.create(
                category=extra_category, korean=f'단어{i}', russian=f'слово{i}'
            )
            UserWordProgress.objects.create(
                user=user, word=filler, learned=True, learned_at=timezone.now()
            )

        apply_review(user, new_word.id, 'easy')

        assert user.achievements.filter(code='ten_words').exists()

    def test_invalid_action_raises(self, prog):
        with pytest.raises(InvalidReviewAction):
            apply_review(prog.user, prog.word_id, 'hack')

    def test_unknown_word_returns_none(self, user):
        assert apply_review(user, 999999, 'good') is None


@pytest.mark.django_db
class TestPendingCount:
    def test_counts_only_due_unlearned(self, user, word):
        future_prog = UserWordProgress.objects.create(
            user=user, word=word,
            next_review=timezone.now() + timezone.timedelta(hours=1),
        )
        assert pending_review_count(user) == 0

        future_prog.next_review = timezone.now() - timezone.timedelta(minutes=1)
        future_prog.save(update_fields=['next_review'])
        assert pending_review_count(user) == 1

        apply_review(user, word.id, 'easy')
        assert pending_review_count(user) == 0
