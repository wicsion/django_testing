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

    cls.list_url = reverse('notes:list')
    cls.add_url = reverse('notes:add')
    cls.success_url = reverse('notes:success')
    cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
    cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
    cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    cls.home_url = reverse('notes:home')
    cls.login_url = reverse('users:login')
    cls.logout_url = reverse('users:logout')
    cls.signup_url = reverse('users:signup')

    cls.form_data = {
        'title': 'Новая заметка',
        'text': 'Текст новой заметки',
        'slug': 'novaya-zametka',
    }
