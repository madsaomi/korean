from rest_framework import serializers
from django.contrib.auth.models import User
from vocabulary.models import Category, Word
from lessons.models import Course, Lesson, LessonStep
from grammar.models import GrammarTopic, GrammarRule, GrammarExercise
from quiz.models import Quiz, Question, Answer
from progress.models import UserLessonProgress, UserWordProgress, UserQuizResult
from library.models import ReadingProgress, Bookmark, Note, LibraryTag
from accounts.models import UserProfile, Streak, Achievement, DailyGoal


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = '__all__'


class StreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = Streak
        fields = '__all__'


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = '__all__'


class DailyGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyGoal
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    word_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'order', 'word_count']

    def get_word_count(self, obj):
        return obj.words.count()


class WordSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Word
        fields = '__all__'


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
        return obj.lessons.count()


class LessonStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonStep
        fields = '__all__'


class LessonSerializer(serializers.ModelSerializer):
    steps = LessonStepSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = '__all__'


class LessonListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'order', 'created_at']


class GrammarRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrammarRule
        fields = '__all__'


class GrammarTopicSerializer(serializers.ModelSerializer):
    rules = GrammarRuleSerializer(many=True, read_only=True)
    rule_count = serializers.SerializerMethodField()

    class Meta:
        model = GrammarTopic
        fields = ['id', 'title', 'slug', 'icon', 'description', 'level', 'order', 'rules', 'rule_count']

    def get_rule_count(self, obj):
        return obj.rules.count()


class GrammarExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrammarExercise
        fields = '__all__'


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text', 'is_correct', 'explanation']


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = '__all__'


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'level', 'time_limit', 'passing_score', 'order', 'questions', 'question_count']

    def get_question_count(self, obj):
        return obj.questions.count()


class QuizListSerializer(serializers.ModelSerializer):
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'level', 'time_limit', 'passing_score', 'order', 'question_count']

    def get_question_count(self, obj):
        return obj.questions.count()


class UserLessonProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)

    class Meta:
        model = UserLessonProgress
        fields = '__all__'


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
        fields = '__all__'


class ReadingProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingProgress
        fields = '__all__'


class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = '__all__'


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = '__all__'


class LibraryTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryTag
        fields = '__all__'


class ReviewActionSerializer(serializers.Serializer):
    word_id = serializers.IntegerField()
    action = serializers.ChoiceField(choices=['again', 'good', 'easy'])
