from django.utils import timezone
from progress.models import UserWordProgress


def pending_review_count(request):
    if request.user.is_authenticated:
        session = getattr(request, 'session', None)
        if session is None:
            return {}
        last_check = session.get('review_check_ts', 0)
        now = timezone.now().timestamp()
        if now - last_check < 60:
            return {'pending_review_count': session.get('review_count_cache', 0)}
        count = UserWordProgress.objects.filter(
            user=request.user, next_review__lte=timezone.now(), learned=False
        ).count()
        session['review_check_ts'] = now
        session['review_count_cache'] = count
        return {'pending_review_count': count}
    return {}
