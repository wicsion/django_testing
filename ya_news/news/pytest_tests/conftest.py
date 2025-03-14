import pytest
from datetime import datetime, timedelta

from django.urls import reverse
from django.test.client import Client
from django.utils import timezone

from news.models import News, Comment
from notes.models import Note


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news(db):
    return News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )


@pytest.fixture
def comment(author, news, db):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def create_news(db, settings):
    today = datetime.today()
    all_news = [
        News(
            title=f'Заголовок {index + 1}',
            text=f'Текст заметки {index + 1}',
            date=today - timedelta(days=index)
        ) for index in range(settings.NEWS_COUNT_ON_HOME_PAGE)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def create_comments(author, news, db):
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Текст комментария {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def comment_data():
    return {
        'text': 'Новый комментарий',
    }


@pytest.fixture
def note_author(author):
    return Note.objects.create(
        title='Заметка автора',
        text='Текст заметки автора',
        author=author,
        slug='zametka-avtora'
    )


@pytest.fixture
def note_data():
    return {
        'title': 'Новая заметка',
        'text': 'Новый текст',
        'slug': 'novaya-zametka'
    }


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def news_detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def notes_list_url():
    return reverse('notes:list')


@pytest.fixture
def add_note_url():
    return reverse('notes:add')


@pytest.fixture
def edit_note_url(note_author):
    return reverse('notes:edit', args=(note_author.slug,))


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def success_url():
    return reverse('notes:success')
