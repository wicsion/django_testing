from http import HTTPStatus

import pytest
from django.test.client import Client
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db

CLIENT = Client()
HTTP_OK = HTTPStatus.OK
HTTP_NOT_FOUND = HTTPStatus.NOT_FOUND


@pytest.mark.parametrize('name', ['home', 'login',
                                  'logout', 'signup', 'detail'])
def test_pages_available_for_anonymous(name, all_routes):
    """Доступные страницы для анонимного пользователя."""
    url = all_routes[name]
    response = CLIENT.get(url)
    assert response.status_code == HTTP_OK


@pytest.mark.parametrize(
    'name, client_fixture, expected_status',
    [
        ('edit', 'not_author_client', HTTP_NOT_FOUND),
        ('delete', 'not_author_client', HTTP_NOT_FOUND),
        ('edit', 'author_client', HTTP_OK),
        ('delete', 'author_client', HTTP_OK),
    ]
)
def test_permissions_for_author_and_not_author(name, client_fixture,
                                               expected_status,
                                               all_routes, request):
    """Проверка прав доступа для авторов и неавторов."""
    client = request.getfixturevalue(client_fixture)
    url = all_routes[name]
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize('name', ['edit', 'delete'])
def test_anonymous_redirects_to_login(client, name, all_routes):
    """Анонимный пользователь перенаправляется на страницу логина."""
    url = all_routes[name]
    login_url = all_routes['login']
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
