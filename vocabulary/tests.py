import pytest
from django.contrib.auth.models import User
from vocabulary.models import Category, Word, WordList


@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='testpass123')


@pytest.fixture
def category():
    return Category.objects.create(name='Еда', slug='food', icon='🍕', order=1)


@pytest.fixture
def word(category):
    return Word.objects.create(
        category=category, korean='밥', russian='рис',
        romanization='bap', level='beginner',
        example_sentence='밥을 먹다', example_translation='есть рис'
    )


@pytest.mark.django_db
class TestCategory:
    def test_create(self, category):
        assert Category.objects.count() == 1
        assert str(category) == 'Еда'

    def test_word_count(self, category, word):
        assert category.words.count() == 1

    def test_ordering(self):
        c1 = Category.objects.create(name='A', slug='a', order=2)
        c2 = Category.objects.create(name='B', slug='b', order=1)
        qs = Category.objects.all()
        assert qs[0] == c2  # lower order first


@pytest.mark.django_db
class TestWord:
    def test_create(self, category, word):
        assert word.korean == '밥'
        assert word.russian == 'рис'

    def test_category_relation(self, word, category):
        assert word.category == category

    def test_level_default(self, category):
        w = Word.objects.create(category=category, korean='test', russian='тест')
        assert w.level == 'beginner'


@pytest.mark.django_db
class TestWordList:
    def test_create_list(self, user):
        wl = WordList.objects.create(user=user, name='Мои слова')
        assert wl.words.count() == 0

    def test_add_word(self, user, word):
        wl = WordList.objects.create(user=user, name='Мои слова')
        wl.words.add(word)
        assert wl.words.count() == 1

    def test_words_in_list(self, user, word):
        wl = WordList.objects.create(user=user, name='Мои слова')
        wl.words.add(word)
        assert list(word.word_lists.all()) == [wl]


@pytest.mark.django_db
class TestVocabularyViews:
    def test_category_list(self, client, category):
        resp = client.get('/vocabulary/')
        assert resp.status_code == 200

    def test_category_detail(self, client, category, word):
        resp = client.get(f'/vocabulary/{category.slug}/')
        assert resp.status_code == 200

    def test_word_search(self, client, word):
        resp = client.get('/vocabulary/search/?q=밥')
        assert resp.status_code == 200
