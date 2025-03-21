from http import HTTPStatus

import pytest
from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_pages_paginator(client, home_url, create_news):
    """Тест количества новостей на странице."""
    response = client.get(home_url)
    assert response.status_code == HTTPStatus.OK
    assert 'object_list' in response.context
    count = response.context['object_list'].count()
    assert count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_order_news_on_page(client, home_url, create_news):
    """Тест сортировки новостей по убыванию даты."""
    response = client.get(home_url)
    assert response.status_code == HTTPStatus.OK
    assert 'object_list' in response.context
    all_dates = [news.date for news in response.context['object_list']]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_order_comment_in_news(client, detail_url, news, create_comments):
    """Тест сортировки комментариев по возрастанию даты."""
    response = client.get(detail_url)
    assert response.status_code == HTTPStatus.OK
    assert 'news' in response.context
    all_comments = response.context['news'].comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.parametrize(
    'client_fixture, have_form',
    [
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False),
    ]
)
def test_contains_form_user_and_anonymous(client_fixture,
                                          detail_url, news, have_form):
    """Проверка наличия формы в зависимости от типа пользователя."""
    response = client_fixture.get(detail_url)
    assert response.status_code == HTTPStatus.OK

    has_form_in_context = 'form' in response.context
    assert has_form_in_context == have_form

    if have_form:
        assert isinstance(response.context['form'], CommentForm)
