from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.models import Achievement, DailyGoal, Streak, UserProfile
from grammar.models import GrammarExercise, GrammarTopic
from lessons.models import Course, Lesson
from library.models import Bookmark, LibraryTag, Note, ReadingProgress
from progress.models import UserLessonProgress, UserQuizResult, UserWordProgress
from quiz.models import Quiz
from review.services import InvalidReviewAction, WordNotDue, apply_review
from vocabulary.models import Category, Word

from . import serializers


def _request_language(request):
    """Return a valid library language from the request, or None."""
    lang = (
        request.data.get('language')
        if hasattr(request, 'data')
        else None
    ) or request.query_params.get('language') or 'ko'
    return lang if lang in ('ko', 'ja') else None


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.annotate(words_count=Count('words')).order_by('order', 'pk')
    serializer_class = serializers.CategorySerializer
    lookup_field = 'slug'


class WordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Word.objects.select_related('category').all()
    serializer_class = serializers.WordSerializer
    filterset_fields = ['category', 'level', 'category__slug']
    search_fields = ['korean', 'russian', 'romanization']
    ordering_fields = ['korean', 'level', 'created_at']


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Course.objects.prefetch_related('lessons')
        .annotate(lessons_count=Count('lessons'))
        .order_by('order', 'pk')
    )
    serializer_class = serializers.CourseSerializer
    filterset_fields = ['level']
    ordering_fields = ['order']


class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Lesson.objects.prefetch_related('steps').all()
    serializer_class = serializers.LessonSerializer
    filterset_fields = ['course', 'course__level']

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.LessonListSerializer
        return serializers.LessonSerializer


class GrammarTopicViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        GrammarTopic.objects.prefetch_related('rules')
        .annotate(rules_count=Count('rules'))
        .order_by('order', 'pk')
    )
    serializer_class = serializers.GrammarTopicSerializer
    lookup_field = 'slug'
    filterset_fields = ['level']
    ordering_fields = ['order']


class GrammarExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GrammarExercise.objects.all()
    serializer_class = serializers.GrammarExerciseSerializer
    filterset_fields = ['topic', 'difficulty', 'topic__slug']


class QuizViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Quiz.objects.prefetch_related('questions__answers')
        .annotate(questions_count=Count('questions'))
        .order_by('order', 'pk')
    )
    serializer_class = serializers.QuizSerializer
    filterset_fields = ['level', 'lesson']

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.QuizListSerializer
        return serializers.QuizSerializer


class ProgressViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        return None

    @action(detail=False)
    def overview(self, request):
        user = request.user
        streak, _ = Streak.objects.get_or_create(user=user)
        goal, _ = DailyGoal.objects.get_or_create(user=user)
        words_learned = UserWordProgress.objects.filter(user=user, learned=True).count()
        quizzes_taken = UserQuizResult.objects.filter(user=user).count()
        lessons_completed = UserLessonProgress.objects.filter(user=user, completed=True).count()
        avg_score = UserQuizResult.objects.filter(user=user).aggregate(
            total_score=Sum('score'), total=Sum('total')
        )
        avg_pct = int((avg_score['total_score'] / avg_score['total']) * 100) if avg_score['total'] else 0

        return Response({
            'streak': serializers.StreakSerializer(streak).data,
            'goal': serializers.DailyGoalSerializer(goal).data,
            'stats': {
                'words_learned': words_learned,
                'quizzes_taken': quizzes_taken,
                'lessons_completed': lessons_completed,
                'avg_quiz_score': avg_pct,
            }
        })

    @action(detail=False)
    def words(self, request):
        qs = UserWordProgress.objects.filter(user=request.user).select_related('word__category')
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = serializers.UserWordProgressSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serializers.UserWordProgressSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def quizzes(self, request):
        qs = UserQuizResult.objects.filter(user=request.user)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = serializers.UserQuizResultSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serializers.UserQuizResultSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def lessons(self, request):
        qs = UserLessonProgress.objects.filter(user=request.user)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = serializers.UserLessonProgressSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serializers.UserLessonProgressSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def achievements(self, request):
        qs = Achievement.objects.filter(user=request.user)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = serializers.AchievementSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serializers.AchievementSerializer(qs, many=True)
        return Response(serializer.data)


class ReviewViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.ReviewActionSerializer

    def list(self, request):
        now = timezone.now()
        due = UserWordProgress.objects.filter(
            user=request.user, next_review__lte=now
        ).select_related('word__category')[:20]
        serializer = serializers.UserWordProgressSerializer(due, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = serializers.ReviewActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        word_id = serializer.validated_data['word_id']
        action = serializer.validated_data['action']

        try:
            prog = apply_review(request.user, word_id, action)
        except InvalidReviewAction:
            return Response({'error': 'Invalid action'}, status=400)
        except WordNotDue:
            return Response({'error': 'Word is not due for review yet'}, status=400)

        if prog is None:
            return Response({'error': 'Word not found in review queue'}, status=404)

        return Response({
            'success': True,
            'action': action,
            'learned': prog.learned,
            'next_review': prog.next_review,
        })


class LibraryViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def list(self, request):
        slugs = ReadingProgress.objects.filter(user=request.user).values_list('slug', flat=True)
        return Response({'reading_slugs': list(slugs)})

    @action(detail=False, methods=['get', 'post'])
    def progress(self, request):
        if request.method == 'POST':
            lang = _request_language(request)
            slug = request.data.get('slug')
            if not slug:
                return Response({'error': 'slug required'}, status=400)
            if lang is None:
                return Response({'error': 'invalid language'}, status=400)
            read_flag = bool(request.data.get('read', True))
            now = timezone.now()
            obj, created = ReadingProgress.objects.get_or_create(
                user=request.user, language=lang, slug=slug,
                defaults={'read': read_flag, 'read_at': now if read_flag else None},
            )
            if not created and obj.read != read_flag:
                obj.read = read_flag
                obj.read_at = now if read_flag else None
                obj.save(update_fields=['read', 'read_at'])
            return Response(serializers.ReadingProgressSerializer(obj).data)
        qs = ReadingProgress.objects.filter(user=request.user)
        return Response(serializers.ReadingProgressSerializer(qs, many=True).data)

    @action(detail=False, methods=['get', 'post', 'delete'])
    def bookmarks(self, request):
        if request.method == 'POST':
            lang = _request_language(request)
            slug = request.data.get('slug')
            if not slug:
                return Response({'error': 'slug required'}, status=400)
            if lang is None:
                return Response({'error': 'invalid language'}, status=400)
            defaults = {
                'title': request.data.get('title') or slug,
                'anchor': request.data.get('anchor', ''),
                'note': request.data.get('note', ''),
            }
            obj, created = Bookmark.objects.get_or_create(
                user=request.user, language=lang, slug=slug,
                defaults=defaults,
            )
            return Response(
                serializers.BookmarkSerializer(obj).data,
                status=201 if created else 200,
            )
        if request.method == 'DELETE':
            pk = request.data.get('id') or request.query_params.get('id')
            try:
                pk = int(pk)
            except (TypeError, ValueError):
                return Response({'error': 'id required'}, status=400)
            deleted, _ = Bookmark.objects.filter(user=request.user, id=pk).delete()
            return Response(status=204) if deleted else Response({'error': 'not found'}, status=404)
        qs = Bookmark.objects.filter(user=request.user)
        return Response(serializers.BookmarkSerializer(qs, many=True).data)

    @action(detail=False, methods=['get', 'post', 'delete'])
    def notes(self, request):
        if request.method == 'POST':
            lang = _request_language(request)
            slug = request.data.get('slug')
            content = (request.data.get('content') or '').strip()
            if not slug:
                return Response({'error': 'slug required'}, status=400)
            if lang is None:
                return Response({'error': 'invalid language'}, status=400)
            if not content:
                return Response({'error': 'content required'}, status=400)
            obj = Note.objects.create(
                user=request.user,
                language=lang,
                slug=slug,
                content=content,
                anchor=request.data.get('anchor', ''),
                highlighted_text=request.data.get('highlighted_text', ''),
            )
            return Response(serializers.NoteSerializer(obj).data, status=201)
        if request.method == 'DELETE':
            pk = request.data.get('id') or request.query_params.get('id')
            try:
                pk = int(pk)
            except (TypeError, ValueError):
                return Response({'error': 'id required'}, status=400)
            deleted, _ = Note.objects.filter(user=request.user, id=pk).delete()
            return Response(status=204) if deleted else Response({'error': 'not found'}, status=404)
        qs = Note.objects.filter(user=request.user)
        return Response(serializers.NoteSerializer(qs, many=True).data)

    @action(detail=False, methods=['get', 'post'])
    def tags(self, request):
        if request.method == 'POST':
            lang = _request_language(request)
            slug = request.data.get('slug')
            tag = (request.data.get('tag') or '').strip().lower()
            if not slug:
                return Response({'error': 'slug required'}, status=400)
            if lang is None:
                return Response({'error': 'invalid language'}, status=400)
            if not tag:
                return Response({'error': 'tag required'}, status=400)
            obj, _ = LibraryTag.objects.get_or_create(
                user=request.user, language=lang, slug=slug, tag=tag)
            return Response(serializers.LibraryTagSerializer(obj).data, status=201)
        qs = LibraryTag.objects.filter(user=request.user)
        return Response(serializers.LibraryTagSerializer(qs, many=True).data)


class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.UserSerializer

    def list(self, request):
        return Response(serializers.UserSerializer(request.user).data)

    @action(detail=False)
    def profile(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        return Response(serializers.UserProfileSerializer(profile).data)
