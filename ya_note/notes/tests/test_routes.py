from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestFixtures(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author_user')
        cls.reader = User.objects.create(username='reader_user')
        cls.note_author = Note.objects.create(
            title='Заметка автора',
            text='Текст заметки автора',
            author=cls.author
        )
        cls.note_reader = Note.objects.create(
            title='Заметка читателя',
            text='Текст заметки читателя',
            author=cls.reader
        )


class TestRoutes(TestFixtures):

    def test_pages_availability_for_anonymous_user(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                self.assertEqual(
                    self.client.get(reverse(name, args=args)).status_code,
                    HTTPStatus.OK
                )

    def test_pages_availability_for_authorized_users(self):
        self.client.force_login(self.reader)
        urls = (
            ('notes:success', None),
            ('notes:list', None),
            ('notes:add', None)
        )
        for name, args in urls:
            with self.subTest(name=name):
                self.assertEqual(
                    self.client.get(reverse(name, args=args)).status_code,
                    HTTPStatus.OK
                )

    def test_pages_availability_for_different_users(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    self.assertEqual(
                        self.client.get(
                            reverse(name, args=(self.note_author.slug,))
                        ).status_code,
                        status
                    )

    def test_redirect_for_anonymous_client(self):
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
                self.assertRedirects(
                    self.client.get(reverse(name, args=args)),
                    f'{login_url}?next={reverse(name, args=args)}'
                )
