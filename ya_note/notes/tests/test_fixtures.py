from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify
from django.test import Client

from notes.models import Note


class BaseTestSetUp(TestCase):
    """Базовая фикстура для всех тестов."""
    NOTE_TEXT = 'текст'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.user = User.objects.create(username='Reader')
        cls.author_client, cls.user_client = Client(), Client()
        cls.author_client.force_login(cls.author)
        cls.user_client.force_login(cls.user)
        cls.notes = Note.objects.create(
            title='Название заметки',
            text='Подробности',
            slug=slugify('Заголовок'),
            author=cls.author
        )
        cls.urls = {
            'list': reverse('notes:list'),
            'add': reverse('notes:add'),
            'success': reverse('notes:success'),
            'detail': reverse('notes:detail', args=(cls.notes.slug,)),
            'edit': reverse('notes:edit', args=(cls.notes.slug,)),
            'delete': reverse('notes:delete', args=(cls.notes.slug,)),
        }
        cls.auth_and_home_urls = {
            'home': reverse('notes:home'),
            'login': reverse('users:login'),
            'logout': reverse('users:logout'),
            'signup': reverse('users:signup'),
        }
        cls.form_data = {
            'text': cls.NOTE_TEXT,
            'title': 'title',
            'slug': 'slug',
        }
