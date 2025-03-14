import pytest
from datetime import datetime, timedelta

from django.test.client import Client
from django.utils import timezone

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):  # Вызываем фикстуру автора.
    # Создаём новый экземпляр клиента, чтобы не менять глобальный.
    client = Client()
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)  # Логиним обычного пользователя в клиенте.
    return client


@pytest.fixture
def news(db):
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def comment(author, news, db):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def create_news(db):
    today = datetime.today()
    all_news = [
        News(
            title=f'Заголовок {index+1}',
            text=f'Текст заметки {index+1}',
            date=today - timedelta(days=index)
        ) for index in range(15)
    ]
    News.objects.bulk_create(all_news)
    return News.objects.all()


@pytest.fixture
def create_comments(author, news, db):
    now = timezone.now()
    for index in range(3):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст комментария {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return news.comment_set.all()


@pytest.fixture
def comment_data():
    return {
        'text': 'Новый комментарий',
    }
