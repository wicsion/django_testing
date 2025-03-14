from http import HTTPStatus

import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def news_detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.mark.django_db
def test_news_count(client, create_news, home_url):
    """На главной странице не более NEWS_COUNT_ON_HOME_PAGE новостей."""
    response = client.get(home_url)
    assert 'object_list' in response.context
    assert (
        response.context['object_list'].count()
        == settings.NEWS_COUNT_ON_HOME_PAGE
    )


@pytest.mark.django_db
def test_news_order_on_home_page(client, create_news, home_url):
    """Новости отсортированы по убыванию даты."""
    response = client.get(home_url)
    news_list = list(response.context['object_list'])
    sorted_news = sorted(news_list, key=lambda news: news.date, reverse=True)
    assert news_list == sorted_news


@pytest.mark.django_db
def test_comments_order_on_news_page(client, create_comments, news_detail_url):
    """Комментарии отсортированы по дате (по возрастанию)."""
    response = client.get(news_detail_url)
    assert response.status_code == HTTPStatus.OK
    assert 'news' in response.context
    comments = response.context['news'].comment_set.all()
    timestamps = [comment.created for comment in comments]
    assert timestamps == sorted(timestamps)


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news_detail_url):
    """Анонимный пользователь не видит форму комментария."""
    response = client.get(news_detail_url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(not_author_client, news_detail_url):
    """Авторизованный пользователь видит форму комментария."""
    response = not_author_client.get(news_detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
