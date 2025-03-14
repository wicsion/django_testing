from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Создаем данные для тестов."""
        cls.author = User.objects.create(username='author_user')
        cls.reader = User.objects.create(username='reader_user')
        cls.note_author = Note.objects.create(
            title='Заметка автора',
            text='Текст заметки автора',
            author=cls.author,
            slug='zametka-avtora'
        )
        cls.note_reader = Note.objects.create(
            title='Заметка читателя',
            text='Текст заметки читателя',
            author=cls.reader,
            slug='zametka-chitatelya'
        )

    def test_pages_availability_for_anonymous_user(self, home_url, login_url, logout_url, signup_url):
        """
        Проверяем доступность страниц для анонимного пользователя.
        """
        urls = (
            home_url,
            login_url,
            logout_url,
            signup_url,
        )
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(
                    self.client.get(url).status_code,
                    HTTPStatus.OK
                )

    def test_pages_availability_for_authorized_users(self, reader_client, success_url, notes_list_url, add_note_url):
        """
        Проверяем доступность страниц для авторизованного пользователя.
        """
        urls = (
            success_url,
            notes_list_url,
            add_note_url,
        )
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(
                    reader_client.get(url).status_code,
                    HTTPStatus.OK
                )

    def test_pages_availability_for_different_users(self, author_client, reader_client, note_author):
        """
        Проверяем доступность страниц для разных пользователей.
        """
        users_statuses = (
            (author_client, HTTPStatus.OK),
            (reader_client, HTTPStatus.NOT_FOUND),
        )
        for client, status in users_statuses:
            for name in ('notes:edit', 'notes:delete', 'notes:detail'):
                with self.subTest(client=client, name=name):
                    self.assertEqual(
                        client.get(reverse(name, args=(note_author.slug,))).status_code,
                        status
                    )

    def test_redirect_for_anonymous_client(self, login_url, note_author):
        """
        Проверяем редирект анонимного пользователя на страницу входа.
        """
        urls = (
            ('notes:edit', (note_author.slug,)),
            ('notes:delete', (note_author.slug,)),
            ('notes:detail', (note_author.slug,)),
            ('notes:add', ()),
            ('notes:list', ()),
            ('notes:success', ()),
        )
        for name, args in urls:
            with self.subTest(name=name):
                self.assertRedirects(
                    self.client.get(reverse(name, args=args)),
                    f'{login_url}?next={reverse(name, args=args)}'
                )
