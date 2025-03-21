from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url_fixture',
    [
        pytest.lazy_fixture('home_url'),
        pytest.lazy_fixture('detail_url'),
        pytest.lazy_fixture('login_url'),
        pytest.lazy_fixture('logout_url'),
        pytest.lazy_fixture('signup_url'),
    ]
)
def test_pages_available_for_anonymous(client, url_fixture):
    """Проверка доступности публичных страниц для анонимного пользователя."""
    response = client.get(url_fixture)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'client_fixture, url_fixture, expected_status',
    [
        (pytest.lazy_fixture('not_author_client'),
         pytest.lazy_fixture('edit_url'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('not_author_client'),
         pytest.lazy_fixture('delete_url'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'),
         pytest.lazy_fixture('edit_url'), HTTPStatus.OK),
        (pytest.lazy_fixture('author_client'),
         pytest.lazy_fixture('delete_url'), HTTPStatus.OK),
    ]
)
def test_permissions_for_author_and_not_author(client_fixture,
                                               url_fixture, expected_status):
    """Проверка доступа к редактированию и удалению комментариев:
    - автору доступно;
    - неавтору — 404.
    """
    response = client_fixture.get(url_fixture)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_fixture',
    [
        pytest.lazy_fixture('edit_url'),
        pytest.lazy_fixture('delete_url'),
    ]
)
def test_anonymous_redirects_to_login(client, url_fixture, login_url):
    """Анонимный пользователь должен быть перенаправлен на логин."""
    expected_redirect = f'{login_url}?next={url_fixture}'
    response = client.get(url_fixture)
    assertRedirects(response, expected_redirect)
