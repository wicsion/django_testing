from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author_user')
        cls.reader = User.objects.create(username='reader_user')
        cls.note_author = Note.objects.create(
            title='Заметка автора',
            text='Текст заметки автора',
            author=cls.author
        )

    def test_note_creation(self):
        self.client.force_login(self.author)
        new_note = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
            'slug': 'novaia-zametka'
        }
        initial_count = Note.objects.count()
        response = self.client.post(reverse('notes:add'), data=new_note)
        self.assertEqual(Note.objects.count(), initial_count + 1)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_note_authorization(self):
        self.client.force_login(self.reader)
        response = self.client.get(reverse('notes:detail',
                                           args=(self.note_author.slug,)))
        self.assertEqual(response.status_code, HTTPStatus.OK)
