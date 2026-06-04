from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.utils import timezone
from .models import Course, Lesson, LessonStep
from progress.models import UserLessonProgress

def lesson_list(request):
    courses = Course.objects.annotate(lesson_count=Count('lessons')).prefetch_related('lessons')
    return render(request, 'lessons/list.html', {'courses': courses})

@login_required
def lesson_detail(request, course_id, lesson_id=None):
    course = get_object_or_404(Course, id=course_id)
    lessons = list(course.lessons.all())

    if lesson_id:
        lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    else:
        lesson = lessons[0] if lessons else None

    steps = lesson.steps.all() if lesson else []

    current_idx = None
    prev_lesson = None
    next_lesson = None
    if lesson and lessons:
        for i, l in enumerate(lessons):
            if l.id == lesson.id:
                current_idx = i
                prev_lesson = lessons[i - 1] if i > 0 else None
                next_lesson = lessons[i + 1] if i < len(lessons) - 1 else None
                break

    if lesson:
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
