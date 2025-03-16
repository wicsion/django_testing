from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note
from notes.tests.test_routes import TestFixtures

User = get_user_model()


class TestLogic(TestFixtures):

    def test_not_unique_slug(self):
        self.client.force_login(self.author)
        note_count_before = Note.objects.count()
        form_data = {
            'title': self.note_author.title,
            'text': 'Повторный текст',
            'slug': self.note_author.slug,
        }
        response = self.client.post(reverse('notes:add'), data=form_data)
        self.assertFormError(
            response,
            'form',
            'slug',
            errors='Заметка с таким slug существует, придумайте значение!'
        )
        assert Note.objects.count() == note_count_before

    def test_slug_automatic_generation(self):
        Note.objects.all().delete()
        self.client.force_login(self.author)
        form_data = {
            'title': 'Автогенерация',
            'text': 'Текст для автослага',
        }
        self.client.post(reverse('notes:add'), data=form_data)
        note = Note.objects.get()
        assert note.slug == slugify(form_data['title'])

    def test_note_creation_with_author(self):
        Note.objects.all().delete()
        self.client.force_login(self.reader)
        form_data = {
            'title': 'Новая заметка',
            'text': 'Новый текст',
            'slug': 'new-slug',
        }
        self.client.post(reverse('notes:add'), data=form_data)
        note = Note.objects.get()
        assert note.title == form_data['title']
        assert note.text == form_data['text']
        assert note.slug == form_data['slug']
        assert note.author == self.reader

    def test_anonymous_user_cant_create_note(self):
        note_count_before = Note.objects.count()
        form_data = {
            'title': 'Анонимная',
            'text': 'Текст',
            'slug': 'anonymous',
        }
        self.client.post(reverse('notes:add'), data=form_data)
        assert Note.objects.count() == note_count_before

    def test_author_can_edit_note(self):
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=(self.note_author.slug,))
        form_data = {
            'title': 'Обновление заголовка',
            'text': 'Новый текст',
            'slug': self.note_author.slug,
        }
        self.client.post(url, data=form_data)
        self.note_author.refresh_from_db()
        assert self.note_author.title == form_data['title']
        assert self.note_author.text == form_data['text']

    def test_reader_cant_edit_note(self):
        self.client.force_login(self.reader)
        url = reverse('notes:edit', args=(self.note_author.slug,))
        old_note = Note.objects.get(pk=self.note_author.pk)
        form_data = {
            'title': 'Попытка редактирования',
            'text': 'Новый текст',
            'slug': self.note_author.slug,
        }
        response = self.client.post(url, data=form_data)
        assert response.status_code == HTTPStatus.NOT_FOUND
        updated_note = Note.objects.get(pk=self.note_author.pk)
        assert updated_note.title == old_note.title
        assert updated_note.text == old_note.text

    def test_author_can_delete_note(self):
        note_count_before = Note.objects.count()
        self.client.force_login(self.author)
        url = reverse('notes:delete', args=(self.note_author.slug,))
        response = self.client.post(url)
        assert response.status_code == HTTPStatus.FOUND
        assert Note.objects.count() == note_count_before - 1

    def test_reader_cant_delete_note(self):
        note_count_before = Note.objects.count()
        self.client.force_login(self.reader)
        url = reverse('notes:delete', args=(self.note_author.slug,))
        response = self.client.post(url)
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert Note.objects.count() == note_count_before
