from http import HTTPStatus
from django.contrib.auth import get_user_model
from .fixtures import BaseTestSetUp

User = get_user_model()


class TestRoutes(BaseTestSetUp):
    """Класс тестирования маршрутов."""

    def test_home_and_auth_pages(self):
        """Тест главной страницы и страниц авторизации."""
        urls_to_test = (
            self.home_url,
            self.login_url,
            self.logout_url,
            self.signup_url,
        )
        for url in urls_to_test:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_delete_detail_pages(self):
        """Тест страниц редактирования, удаления и деталей заметки."""
        users_status = (
            (self.author_client, HTTPStatus.OK),
            (self.user_client, HTTPStatus.NOT_FOUND),
        )
        urls_to_test = (
            self.detail_url,
            self.edit_url,
            self.delete_url,
        )
        for client, status in users_status:
            for url in urls_to_test:
                with self.subTest(client=client, url=url):
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_list_add_done_pages(self):
        """Тест страниц списка заметок, добавления и успешного добавления."""
        urls_to_test = (
            self.list_url,
            self.add_url,
            self.success_url,
        )
        for url in urls_to_test:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_anonymous_user(self):
        """Тест на редирект анонимного пользователя."""
        login_url = self.login_url
        urls_to_test = (
            self.list_url,
            self.add_url,
            self.success_url,
            self.detail_url,
            self.edit_url,
            self.delete_url,
        )
        for url in urls_to_test:
            with self.subTest(url=url):
                response = self.client.get(url)
                redirect_url = f'{login_url}?next={url}'
                self.assertRedirects(response, redirect_url)
