from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """Тестируем доступность страниц для различных пользователей."""

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для тестов: пользователи и заметки."""
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

    def test_pages_availability_for_anonymous_user(self):
        """Проверяем доступность страниц для анонимных пользователей."""
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(
                    response.status_code, HTTPStatus.OK,
                    f'Страница {url} недоступна для анонимного пользователя.'
                )

    def test_pages_availability_for_authorized_users(self):
        """Проверяем доступность страниц для авторизованных пользователей."""
        self.client.force_login(self.reader)
        urls = (
            ('notes:success', None),
            ('notes:list', None),
            ('notes:add', None)
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        """Проверяем доступность страниц для разных пользователей."""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete', 'notes:detail'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note_author.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Проверяем редирект для анонимных пользователей."""
        login_url = reverse('users:login')
        urls = (
            ('notes:edit', (self.note_author.slug,)),
            ('notes:delete', (self.note_author.slug,)),
            ('notes:detail', (self.note_author.slug,)),
            ('notes:add', ()),
            ('notes:list', ()),
            ('notes:success', ()),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
