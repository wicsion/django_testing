from http import HTTPStatus

import pytest
from django.conf import settings

from news.forms import CommentForm


pytestmark = pytest.mark.django_db


def test_pages_paginator(client, routes_for_paginator, create_news):
    """Тест количества новостей на странице."""
    url = routes_for_paginator['home']
    response = client.get(url)
    count = response.context['object_list'].count()
    assert response.status_code == HTTPStatus.OK
    assert count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_order_news_on_page(client, all_routes, create_news):
    """Тест, сортировка новостей по убыванию."""
    url = all_routes['home']
    response = client.get(url)
    all_dates = [news.date for news in response.context['object_list']]
    sorted_dates = sorted(all_dates, reverse=True)
    assert response.status_code == HTTPStatus.OK
    assert all_dates == sorted_dates


def test_order_comment_in_news(client, all_routes, news, create_comments):
    """Тест сортировка по возрастанию комментов."""
    url = all_routes['detail']
    response = client.get(url)
    all_comments = response.context['news'].comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.parametrize(
    'name, have_form',
    [
        (pytest.lazy_fixture('not_author_client'), True),  # пользователь
        (pytest.lazy_fixture('author_client'), True),  # автор
        (pytest.lazy_fixture('client'), False)  # анонимный
    ]
)
def test_contains_form_user_and_anonymous(name, all_routes, news, have_form):
    """Тест юзера, автора, анонима на наличие формы."""
    url = all_routes['detail']
    response = name.get(url)
    # Проверяем наличие формы в контексте ответа
    assert ('form' in response.context) == have_form

    # Если форма должна присутствовать, проверяем её тип
    if have_form:
        assert isinstance(response.context['form'], CommentForm)
