from django.db import transaction
from django.utils import timezone

from progress.models import UserWordProgress
from accounts.utils import check_word_achievements

VALID_ACTIONS = ('again', 'good', 'easy')
BASE_DAYS = [1, 3, 7, 14, 30]
AGAIN_INTERVAL_MINUTES = 10
EASY_INTERVAL_DAYS = 7


class InvalidReviewAction(ValueError):
    pass


@transaction.atomic
def apply_review(user, word_id, action):
    """Apply a review action to a word in the user's queue.

    Returns the updated UserWordProgress instance, or None if the user has
    no progress record for the given word. Raises InvalidReviewAction for
    unknown actions and ValueError/TypeError for malformed word ids.
    """
    if action not in VALID_ACTIONS:
        raise InvalidReviewAction(action)

    word_id = int(word_id)
    prog = (
        UserWordProgress.objects
        .select_for_update()
        .filter(user=user, word_id=word_id)
        .first()
    )
    if prog is None:
        return None

    now = timezone.now()
    if action == 'again':
        # A lapse resets the interval ladder instead of advancing it
        prog.review_count = 0
        prog.next_review = now + timezone.timedelta(minutes=AGAIN_INTERVAL_MINUTES)
    elif action == 'good':
        prog.review_count += 1
        days = BASE_DAYS[min(prog.review_count - 1, len(BASE_DAYS) - 1)]
        prog.next_review = now + timezone.timedelta(days=days)
    else:  # easy
        prog.review_count += 1
        prog.learned = True
        if not prog.learned_at:
            prog.learned_at = now
        prog.next_review = now + timezone.timedelta(days=EASY_INTERVAL_DAYS)

    prog.save(update_fields=['review_count', 'next_review', 'learned', 'learned_at'])

    if prog.learned:
        check_word_achievements(user)

    return prog


def pending_review_count(user):
    return UserWordProgress.objects.filter(
        user=user,
        learned=False,
        next_review__lte=timezone.now(),
    ).count()
