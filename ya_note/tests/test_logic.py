from http import HTTPStatus

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from pytils.translit import slugify

from notes.models import Note

User = get_user_model()

NOTE_DATA = {
    'title': 'Новая заметка',
    'text': 'Новый текст',
    'slug': 'novaia-zametka',
}


class TestLogic(TestCase):
    """Тестируем логику создания заметок и проверки прав пользователей."""

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

    def test_not_unique_slug(self):
        """Проверяем, что при дублировании слага выводится ошибка формы."""
        new_note = {
            'title': 'Заметка автора',
            'text': 'Новый текст',
            'slug': 'zametka-avtora',
        }
        self.client.force_login(self.author)
        response = self.client.post(reverse('notes:add'), data=new_note)
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=('заметка существует, придумайте уникальное значение!')
        )
        self.assertEqual(Note.objects.count(), 2)

    def test_slug_automatic_generation(self):
        """Проверяем автоматическую генерацию слага при создании заметки."""
        new_note = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
        }
        self.client.force_login(self.author)
        self.client.post(reverse('notes:add'), data=new_note)
        new_note_obj = Note.objects.last()
        self.assertEqual(new_note_obj.slug, slugify(new_note_obj.title))

    def test_note_creation_with_author(self):
        """Проверяем, что заметка создается с правильным автором и полями."""
        initial_count = Note.objects.count()
        self.client.force_login(self.reader)
        self.client.post(reverse('notes:add'), data=NOTE_DATA)
        new_note = Note.objects.last()
        self.assertEqual(Note.objects.count(), initial_count + 1)
        self.assertEqual(new_note.author, self.reader)
        self.assertEqual(new_note.title, NOTE_DATA['title'])
        self.assertEqual(new_note.text, NOTE_DATA['text'])
        self.assertEqual(new_note.slug, NOTE_DATA['slug'])

    def test_anonymous_user_cant_create_note(self):
        """Проверяем, что анонимные пользователи не могут создать заметку."""
        initial_count = Note.objects.count()
        response = self.client.post(reverse('notes:add'), data=NOTE_DATA)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), initial_count)

    def test_user_permissions_for_editing_and_deleting_notes(self):
        """Проверяем права пользователей на редактирование заметок."""
        test_cases = (
            (self.reader, 'delete', HTTPStatus.NOT_FOUND),
            (self.reader, 'edit', HTTPStatus.NOT_FOUND),
            (self.author, 'edit', HTTPStatus.OK),
            (self.author, 'delete', HTTPStatus.FOUND),
        )
        for user, action, expected_status in test_cases:
            with self.subTest(user=user, action=action):
                self.client.force_login(user)
                if action == 'delete':
                    url = reverse('notes:delete',
                                  args=(self.note_author.slug,))
                elif action == 'edit':
                    url = reverse('notes:edit', args=(self.note_author.slug,))
                response = self.client.post(url)
                self.assertEqual(response.status_code, expected_status)
