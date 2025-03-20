from http import HTTPStatus

import pytest
from django.test.client import Client
from pytest_django.asserts import assertRedirects
from django.urls import reverse

pytestmark = pytest.mark.django_db

CLIENT = Client()
HTTP_OK = HTTPStatus.OK
HTTP_NOT_FOUND = HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'url_fixture',
    ['home_url', 'detail_url']
)
def test_pages_available_for_anonymous(url_fixture, request):
    """Доступные страницы для анонимного пользователя."""
    url = request.getfixturevalue(url_fixture)
    response = CLIENT.get(url)
    assert response.status_code == HTTP_OK


@pytest.mark.parametrize(
    'name, client_fixture, url_fixture, expected_status',
    [
        ('edit', 'not_author_client', 'edit_url', HTTP_NOT_FOUND),
        ('delete', 'not_author_client', 'delete_url', HTTP_NOT_FOUND),
        ('edit', 'author_client', 'edit_url', HTTP_OK),
        ('delete', 'author_client', 'delete_url', HTTP_OK),
    ]
)
def test_permissions_for_author_and_not_author(
    name, client_fixture, url_fixture, expected_status, request
):
    """Проверка прав доступа для авторов и неавторов."""
    client = request.getfixturevalue(client_fixture)
    url = request.getfixturevalue(url_fixture)
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_fixture',
    ['edit_url', 'delete_url']
)
def test_anonymous_redirects_to_login(client, url_fixture, request):
    """Анонимный пользователь перенаправляется на страницу логина."""
    url = request.getfixturevalue(url_fixture)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
