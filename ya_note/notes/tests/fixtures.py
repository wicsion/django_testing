from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.test import Client

from notes.models import Note


class BaseTestSetUp(TestCase):
    """Базовая настройка для всех тестов."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.user = User.objects.create(username='Reader')
        cls.author_client = Client()
        cls.user_client = Client()
        cls.author_client.force_login(cls.author)
        cls.user_client.force_login(cls.user)

        cls.note = Note.objects.create(
            title='Название заметки',
            text='Подробности',
            slug='zagolovok',
            author=cls.author
        )

        cls.urls = {
            'list': reverse('notes:list'),
            'add': reverse('notes:add'),
            'success': reverse('notes:success'),
            'detail': reverse('notes:detail', args=(cls.note.slug,)),
            'edit': reverse('notes:edit', args=(cls.note.slug,)),
            'delete': reverse('notes:delete', args=(cls.note.slug,)),
        }

        cls.auth_and_home_urls = {
            'home': reverse('notes:home'),
            'login': reverse('users:login'),
            'logout': reverse('users:logout'),
            'signup': reverse('users:signup'),
        }

        cls.form_data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
            'slug': 'novaya-zametka',
        }
