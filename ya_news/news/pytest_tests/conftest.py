from datetime import datetime, timedelta


import pytest
from django.test.client import Client
from django.conf import settings
from django.utils import timezone
from django.urls import reverse

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    """Фикстура автора."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Фикстура пользователя."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """Фикстура залогиненного автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Фикстура залогиненного юзера."""
    client = Client()
    client.force_login(not_author)  # Логиним обычного пользователя в клиенте.
    return client


@pytest.fixture
def news(author):
    """Фикстура новости."""
    news = News.objects.create(  # Создаём объект заметки.
        title='Заголовок',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def comment(news, author):
    """Фикстура коммента."""
    comment = Comment.objects.create(
        text='текст',
        news=news,
        author=author
    )
    return comment


@pytest.fixture
def create_news(db):
    """Фикстура для создания нескольких новостей."""
    News.objects.all().delete()
    today = datetime.today()
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        News.objects.create(
            title=f'Новость {index}',
            text=f'текст {index}',
            date=today - timedelta(days=index)
        )


@pytest.fixture
def create_comments(news, author):
    """Фикстура для создания нескольких комментов."""
    now = timezone.now()
    for index in range(5):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Comment text number {index}'
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def routes_for_paginator():
    return {
        'home': reverse('news:home')
    }


@pytest.fixture
def all_routes(news, comment):
    """Фикстура всех адресов."""
    return {
        'home': reverse('news:home'),
        'detail': reverse('news:detail', args=(news.pk,)),
        'edit': reverse('news:edit', args=(comment.id,)),
        'delete': reverse('news:delete', args=(comment.id,)),
        'login': reverse('users:login'),
        'logout': reverse('users:logout'),
        'signup': reverse('users:signup'),
    }
