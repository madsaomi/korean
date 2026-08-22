from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, render

from progress.models import UserLessonProgress

from .models import Course, Lesson


def lesson_list(request):
    courses = Course.objects.annotate(lesson_count=Count('lessons')).prefetch_related('lessons')
    return render(request, 'lessons/list.html', {'courses': courses})

@login_required
def lesson_detail(request, course_id, lesson_id=None):
    course = get_object_or_404(Course, id=course_id)
    lessons = list(course.lessons.all())

    if not lessons and not lesson_id:
        return render(request, 'lessons/detail.html', {
            'course': course,
            'lesson': None,
            'steps': [],
            'prev_lesson': None,
            'next_lesson': None,
            'lesson_count': 0,
            'current_idx': None,
        })

    if lesson_id:
        lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    else:
        lesson = lessons[0]

    steps = lesson.steps.all()

    current_idx = None
    prev_lesson = None
    next_lesson = None
    for i, l in enumerate(lessons):
        if l.id == lesson.id:
            current_idx = i
            prev_lesson = lessons[i - 1] if i > 0 else None
            next_lesson = lessons[i + 1] if i < len(lessons) - 1 else None
            break

    UserLessonProgress.objects.get_or_create(
        user=request.user, lesson=lesson,
        defaults={'completed': False}
    )

    return render(request, 'lessons/detail.html', {
        'course': course,
        'lesson': lesson,
        'steps': steps,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'lesson_count': len(lessons),
        'current_idx': current_idx,
    })

