# Гайд по тестам

Runner — **только pytest** (`manage.py test` находит 0 тестов: фикстуры pytest
не работают под unittest-раннером). Конфиг в `pytest.ini`: `DJANGO_SETTINGS_MODULE=config.settings`,
testpaths = все приложения.

## Паттерны проекта

Тесты лежат в `tests.py` каждого приложения. Общего conftest.py нет —
фикстуры локальные и копируются по образцу. Пример-эталон: `api/tests.py`.

```python
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='testpass123')

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def category():
    return Category.objects.create(name='Еда', slug='food', icon='🍕', order=1)
```

- Доступ к БД: `@pytest.mark.django_db` на классе или тесте.
- HTML-клиент: встроенный `client` (pytest-django), логин через
  `client.force_login(user)`.
- API: `APIClient` + `force_authenticate`; токен-логин тестируется через
  `/api/api-token-auth/`.
- POST с JSON: `client.post(url, data, content_type='application/json')`.

## Что покрывать в первую очередь

1. Серверные правила из `.agents/conventions.md`: фильтр по request.user,
   400 вместо 500 на мусорный ввод.
2. SRS-лестница (`review/services.py::apply_review`): again сбрасывает счётчик,
   good идёт по [1,3,7,14,30], easy ставит learned. Сейчас НЕ покрыто — это
   главный пробел.
3. Квиз: серверный таймер (просроченная попытка → redirect + отсутствие записи),
   writing-ответы текстом. Тоже нет тестов.
4. Модели/вьюхи при любом изменении — следуй существующему стилю файла.

## Известные дыры покрытия

- `lessons/tests.py` пустой.
- Нет тестов на IDOR (чужой pk должен отдавать 404).
- TTS-эндпоинт тестируется одним запросом (лимит не проверяется).
- При добавлении тестов держи общий счёт зелёным: `.\venv\Scripts\python.exe -m pytest -q`
  (89 passed на момент аудита).

## Подводные камни

- Время: используй `django.utils.timezone`, для дат пользователя —
  `timezone.localdate()`; таймзона проекта Asia/Tashkent.
- Кэш учебника (10 мин) в тестах library лучше обходить напрямую через
  `library.pages.get_all_pages` — он вернёт кэш между тестами; если контент
  важен, очищай `cache.delete('library_pages_ko')` или мочь получить пусто.
- Rate limit TTS живёт в Django cache — между тестами тоже персистит в рамках
  процесса; учитывай при лимитных тестах (`cache.clear()` в фикстуре).
