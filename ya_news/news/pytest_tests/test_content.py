from http import HTTPStatus

import pytest
from django.conf import settings

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, create_news, home_url):
    """На главной отображается не более NEWS_COUNT_ON_HOME_PAGE новостей."""
    response = client.get(home_url)
    assert 'object_list' in response.context
    news_on_page = response.context['object_list']
    assert news_on_page.count() == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order_on_home_page(client, create_news, home_url):
    """Новости на главной странице отсортированы по дате убывания."""
    response = client.get(home_url)
    news_list = response.context['object_list']
    timestamps = [news.date for news in news_list]
    assert timestamps == sorted(timestamps, reverse=True)


@pytest.mark.django_db
def test_comments_order_on_news_page(client, create_comments, news_detail_url):
    """Комментарии на странице новости отсортированы по дате создания."""
    response = client.get(news_detail_url)
    assert response.status_code == HTTPStatus.OK
    assert 'news' in response.context
    news_comments = response.context['news'].comment_set.all()
    timestamps = [comment.created for comment in news_comments]
    assert timestamps == sorted(timestamps)


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news_detail_url):
    """Анонимному пользователю форма комментария недоступна."""
    response = client.get(news_detail_url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(not_author_client, news_detail_url):
    """Авторизованному пользователю форма комментария доступна."""
    response = not_author_client.get(news_detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
