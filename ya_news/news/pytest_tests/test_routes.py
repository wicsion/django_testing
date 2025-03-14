import pytest

from http import HTTPStatus

from django.urls import reverse

from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture


@pytest.mark.parametrize(
    'name',
    ('news:home', 'news:detail', 'users:login', 'users:logout', 'users:signup')
)
@pytest.mark.django_db
def test_pages_availability(client, name, news):
    response = client.get(
        reverse(name, args=(news.id,))
        if name == 'news:detail' else reverse(name)
    )
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_pages_availability_for_different_users(parametrized_client, name,
                                                comment, expected_status):
    response = parametrized_client.get(reverse(name, args=(comment.id,)))
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_redirect_for_anonymous_client(client, name, comment):
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    expected_url = f'{login_url}?next={url}'
    assertRedirects(client.get(url), expected_url)
