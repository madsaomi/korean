from django.contrib.auth.models import User
from rest_framework import serializers

from accounts.models import Achievement, DailyGoal, Streak, UserProfile
from grammar.models import GrammarExercise, GrammarRule, GrammarTopic
from lessons.models import Course, Lesson, LessonStep
from library.models import Bookmark, LibraryTag, Note, ReadingProgress
from progress.models import UserLessonProgress, UserQuizResult, UserWordProgress
from quiz.models import Answer, Question, Quiz
from vocabulary.models import Category, Word


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'native_language', 'level', 'avatar', 'created_at']


class StreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = Streak
        fields = ['id', 'user', 'current_streak', 'longest_streak', 'last_active_date']


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['id', 'user', 'code', 'title', 'description', 'icon', 'earned_at']


class DailyGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyGoal
        fields = ['id', 'user', 'words_target', 'lessons_target', 'quizzes_target', 'updated_at']


class CategorySerializer(serializers.ModelSerializer):
    word_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'order', 'word_count']

    def get_word_count(self, obj):
        count = getattr(obj, 'words_count', None)
        return count if count is not None else obj.words.count()


class WordSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Word
        fields = [
            'id', 'category', 'category_name', 'korean', 'russian',
            'romanization', 'example_sentence', 'example_translation',
            'audio_url', 'level', 'created_at',
        ]


class WordListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = ['id', 'korean', 'russian', 'romanization', 'level']


class CourseSerializer(serializers.ModelSerializer):
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'level', 'order', 'image', 'lesson_count']

    def get_lesson_count(self, obj):
        count = getattr(obj, 'lessons_count', None)
        return count if count is not None else obj.lessons.count()


class LessonStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonStep
        fields = [
            'id', 'lesson', 'step_type', 'title', 'content_korean',
            'content_russian', 'image', 'audio_url', 'order',
        ]


class LessonSerializer(serializers.ModelSerializer):
    steps = LessonStepSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = ['id', 'course', 'title', 'description', 'order', 'created_at', 'steps']


class LessonListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'order', 'created_at']


class GrammarRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrammarRule
        fields = [
            'id', 'topic', 'title', 'explanation', 'formula',
            'examples', 'korean_examples', 'russian_examples', 'order',
        ]


class GrammarTopicSerializer(serializers.ModelSerializer):
    rules = GrammarRuleSerializer(many=True, read_only=True)
    rule_count = serializers.SerializerMethodField()

    class Meta:
        model = GrammarTopic
        fields = ['id', 'title', 'slug', 'icon', 'description', 'level', 'order', 'rules', 'rule_count']

    def get_rule_count(self, obj):
        count = getattr(obj, 'rules_count', None)
        return count if count is not None else obj.rules.count()


class GrammarExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrammarExercise
        fields = [
            'id', 'topic', 'question', 'correct_answer',
            'option_a', 'option_b', 'option_c', 'option_d',
            'explanation', 'difficulty', 'order',
        ]


class AnswerSerializer(serializers.ModelSerializer):
    # is_correct/explanation are deliberately excluded: quiz answers are
    # served to unauthenticated clients and must not leak the key.
    class Meta:
        model = Answer
        fields = ['id', 'text']


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            'id', 'quiz', 'question_type', 'question_korean',
            'question_russian', 'order', 'answers',
        ]


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'level', 'time_limit', 'passing_score', 'order', 'questions', 'question_count']

    def get_question_count(self, obj):
        count = getattr(obj, 'questions_count', None)
        return count if count is not None else obj.questions.count()


class QuizListSerializer(serializers.ModelSerializer):
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'level', 'time_limit', 'passing_score', 'order', 'question_count']

    def get_question_count(self, obj):
        count = getattr(obj, 'questions_count', None)
        return count if count is not None else obj.questions.count()


class UserLessonProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)

    class Meta:
        model = UserLessonProgress
        fields = [
            'id', 'user', 'lesson', 'completed', 'score',
            'completed_at', 'lesson_title',
        ]


class UserWordProgressSerializer(serializers.ModelSerializer):
    word_detail = WordListSerializer(source='word', read_only=True)

    class Meta:
        model = UserWordProgress
        fields = ['id', 'word', 'word_detail', 'learned', 'review_count', 'next_review', 'notes', 'learned_at']


class UserQuizResultSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    percentage = serializers.IntegerField(read_only=True)

    class Meta:
        model = UserQuizResult
        fields = [
            'id', 'user', 'quiz', 'score', 'total',
            'completed_at', 'quiz_title', 'percentage',
        ]


class ReadingProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingProgress
        fields = ['id', 'user', 'language', 'slug', 'read', 'read_at']


class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = [
            'id', 'user', 'language', 'slug', 'title', 'anchor',
            'note', 'color', 'section', 'created_at',
        ]


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = [
            'id', 'user', 'language', 'slug', 'anchor',
            'highlighted_text', 'content', 'created_at', 'updated_at',
        ]


class LibraryTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryTag
        fields = ['id', 'user', 'language', 'slug', 'tag']


class ReviewActionSerializer(serializers.Serializer):
    word_id = serializers.IntegerField()
    action = serializers.ChoiceField(choices=['again', 'good', 'easy'])
