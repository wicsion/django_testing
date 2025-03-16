from http import HTTPStatus

import pytest
from django.test.client import Client
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf


pytestmark = pytest.mark.django_db

CLIENT = Client()
HTTP_OK = HTTPStatus.OK
HTTP_NOT_FOUND = HTTPStatus.NOT_FOUND
NOT_AUTHOR_CLIENT = lf('not_author_client')
AUTHOR_CLIENT = lf('author_client')


@pytest.mark.parametrize(
    'name, user_client, expected_status',
    [
        ('home', CLIENT, HTTP_OK),
        ('login', CLIENT, HTTP_OK),
        ('logout', CLIENT, HTTP_OK),
        ('signup', CLIENT, HTTP_OK),
        ('detail', CLIENT, HTTP_OK),
        ('edit', NOT_AUTHOR_CLIENT, HTTP_NOT_FOUND),
        ('delete', AUTHOR_CLIENT, HTTP_OK),
    ]
)
def test_anonymous_user_access(name, user_client, expected_status, all_routes):
    """Тест доступности страниц для анонимного пользователя."""
    url = all_routes[name]
    response = user_client.get(url)
    assert response.status_code == expected_status


def test_redirect_anonymous_cant_edit_and_del_comment(client, all_routes):
    """Редирект анонима на страницу авторизации."""
    url = all_routes['edit']
    login_url = all_routes['login']
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
