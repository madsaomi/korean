import pytest
from grammar.models import GrammarTopic, GrammarRule, GrammarExercise


@pytest.fixture
def topic():
    topic = GrammarTopic.objects.create(
        title='Падежи', slug='padezhi', icon='📖',
        description='Основные падежи', level='beginner', order=1
    )
    GrammarRule.objects.create(
        topic=topic, title='Именительный падеж',
        explanation='Используется для подлежащего',
        formula='N+가/이', order=1
    )
    GrammarRule.objects.create(
        topic=topic, title='Винительный падеж',
        explanation='Используется для объекта',
        formula='N+을/를', order=2
    )
    return topic


@pytest.mark.django_db
class TestGrammarTopic:
    def test_create(self, topic):
        assert GrammarTopic.objects.count() == 1
        assert str(topic) == 'Падежи'

    def test_rules_relation(self, topic):
        assert topic.rules.count() == 2

    def test_default_level(self):
        t = GrammarTopic.objects.create(title='Test', slug='test')
        assert t.level == 'beginner'


@pytest.mark.django_db
class TestGrammarRule:
    def test_create_rule(self, topic):
        rule = topic.rules.first()
        assert rule.formula == 'N+가/이'

    def test_rule_ordering(self, topic):
        rules = list(topic.rules.all())
        assert rules[0].order == 1
        assert rules[1].order == 2

    def test_str_includes_topic(self, topic):
        rule = topic.rules.first()
        assert 'Падежи' in str(rule)
        assert 'Именительный' in str(rule)


@pytest.mark.django_db
class TestGrammarExercise:
    def test_create_exercise(self, topic):
        ex = GrammarExercise.objects.create(
            topic=topic,
            question='Какой падеж для подлежащего?',
            correct_answer='Именительный',
            option_a='Именительный', option_b='Родительный',
            option_c='Дательный', option_d='Винительный',
            difficulty='beginner'
        )
        assert ex.option_a == 'Именительный'
        assert ex.difficulty == 'beginner'

    def test_exercise_no_topic(self):
        ex = GrammarExercise.objects.create(
            question='Test?',
            correct_answer='A', option_a='A', option_b='B'
        )
        assert ex.topic is None


@pytest.mark.django_db
class TestGrammarViews:
    def test_grammar_list(self, client, topic):
        resp = client.get('/grammar/')
        assert resp.status_code == 200

    def test_grammar_detail(self, client, topic):
        resp = client.get(f'/grammar/{topic.slug}/')
        assert resp.status_code == 200

    def test_exercise_list(self, client):
        resp = client.get('/grammar/exercises/')
        assert resp.status_code == 200
