from rest_framework import viewsets, status, permissions, filters, generics, decorators
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend

from vocabulary.models import Category, Word
from lessons.models import Course, Lesson
from grammar.models import GrammarTopic, GrammarExercise
from quiz.models import Quiz
from progress.models import UserWordProgress, UserQuizResult, UserLessonProgress
from library.models import ReadingProgress, Bookmark, Note, LibraryTag
from accounts.models import UserProfile, Streak, Achievement, DailyGoal
from accounts.utils import check_word_achievements

from . import serializers


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return True


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer
    lookup_field = 'slug'


class WordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Word.objects.select_related('category').all()
    serializer_class = serializers.WordSerializer
    filterset_fields = ['category', 'level', 'category__slug']
    search_fields = ['korean', 'russian', 'romanization']
    ordering_fields = ['korean', 'level', 'created_at']


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.prefetch_related('lessons').all()
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
    queryset = GrammarTopic.objects.prefetch_related('rules').all()
    serializer_class = serializers.GrammarTopicSerializer
    lookup_field = 'slug'
    filterset_fields = ['level']
    ordering_fields = ['order']


class GrammarExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GrammarExercise.objects.all()
    serializer_class = serializers.GrammarExerciseSerializer
    filterset_fields = ['topic', 'difficulty', 'topic__slug']


class QuizViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Quiz.objects.prefetch_related('questions__answers').all()
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
            user=request.user, next_review__lte=now, learned=False
        ).select_related('word__category')[:20]
        serializer = serializers.UserWordProgressSerializer(due, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = serializers.ReviewActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        word_id = serializer.validated_data['word_id']
        action = serializer.validated_data['action']
        now = timezone.now()

        prog = UserWordProgress.objects.filter(user=request.user, word_id=word_id).first()
        if not prog:
            return Response({'error': 'Word not found in review queue'}, status=404)

        prog.review_count += 1
        if action == 'easy':
            prog.next_review = now + timezone.timedelta(days=7)
            prog.learned = True
            if not prog.learned_at:
                prog.learned_at = now
            check_word_achievements(request.user)
        elif action == 'good':
            base_days = [1, 3, 7, 14, 30]
            days = base_days[min(prog.review_count - 1, len(base_days) - 1)]
            prog.next_review = now + timezone.timedelta(days=days)
        elif action == 'again':
            prog.next_review = now + timezone.timedelta(hours=1)
        prog.save(update_fields=['review_count', 'next_review', 'learned', 'learned_at'])

        return Response({'success': True, 'action': action})


class LibraryViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def list(self, request):
        slugs = ReadingProgress.objects.filter(user=request.user).values_list('slug', flat=True)
        return Response({'reading_slugs': list(slugs)})

    @action(detail=False, methods=['get', 'post'])
    def progress(self, request):
        if request.method == 'POST':
            obj, _ = ReadingProgress.objects.get_or_create(
                user=request.user,
                slug=request.data.get('slug'),
                defaults={'read': request.data.get('read', True)}
            )
            if not request.data.get('read', True):
                obj.read = False
                obj.save(update_fields=['read'])
            return Response(serializers.ReadingProgressSerializer(obj).data)
        qs = ReadingProgress.objects.filter(user=request.user)
        return Response(serializers.ReadingProgressSerializer(qs, many=True).data)

    @action(detail=False, methods=['get', 'post', 'delete'])
    def bookmarks(self, request):
        if request.method == 'POST':
            obj = Bookmark.objects.create(
                user=request.user,
                slug=request.data.get('slug'),
                title=request.data.get('title', ''),
                anchor=request.data.get('anchor', ''),
                note=request.data.get('note', ''),
            )
            return Response(serializers.BookmarkSerializer(obj).data, status=201)
        if request.method == 'DELETE':
            pk = request.data.get('id') or request.query_params.get('id')
            if pk:
                Bookmark.objects.filter(user=request.user, id=pk).delete()
                return Response(status=204)
            return Response({'error': 'id required'}, status=400)
        qs = Bookmark.objects.filter(user=request.user)
        return Response(serializers.BookmarkSerializer(qs, many=True).data)

    @action(detail=False, methods=['get', 'post', 'delete'])
    def notes(self, request):
        if request.method == 'POST':
            obj = Note.objects.create(
                user=request.user,
                slug=request.data.get('slug'),
                content=request.data.get('content'),
                anchor=request.data.get('anchor', ''),
                highlighted_text=request.data.get('highlighted_text', ''),
            )
            return Response(serializers.NoteSerializer(obj).data, status=201)
        if request.method == 'DELETE':
            pk = request.data.get('id') or request.query_params.get('id')
            if pk:
                Note.objects.filter(user=request.user, id=pk).delete()
                return Response(status=204)
            return Response({'error': 'id required'}, status=400)
        qs = Note.objects.filter(user=request.user)
        return Response(serializers.NoteSerializer(qs, many=True).data)

    @action(detail=False, methods=['get', 'post'])
    def tags(self, request):
        if request.method == 'POST':
            obj = LibraryTag.objects.create(
                user=request.user,
                slug=request.data.get('slug'),
                tag=request.data.get('tag'),
            )
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
