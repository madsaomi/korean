from django.utils import timezone

def pending_review_count(request):
    if request.user.is_authenticated:
        from progress.models import UserWordProgress
        count = UserWordProgress.objects.filter(
            user=request.user, next_review__lte=timezone.now(), learned=False
        ).count()
        return {'pending_review_count': count}
    return {}
