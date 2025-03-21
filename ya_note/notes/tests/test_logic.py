from http import HTTPStatus

from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING
from .fixtures import BaseTestSetUp


User = get_user_model()


class TestNoteCreate(BaseTestSetUp):
    """Класс теста создания заметки."""

    def test_anonymous_note(self):
        """Тест, аноним не может создать заметку."""
        before_count = Note.objects.count()
        self.client.post(self.add_url, data=self.form_data)
        after_count = Note.objects.count()
        self.assertEqual(before_count, after_count)

    def test_user_can_create_notes(self):
        """Тест, что юзер может создать заметку."""
        Note.objects.all().delete()
        response = self.user_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.author, self.user)
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.slug, self.form_data['slug'])

    def test_auto_slug_creation(self):
        """Тест, что slug создается автоматически, если не заполнен."""
        Note.objects.all().delete()
        self.form_data.pop('slug')
        response = self.user_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)

        note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(note.slug, expected_slug)

    def test_unique_slug(self):
        """Тест, что невозможно создать две заметки с одинаковым slug."""
        self.form_data['slug'] = self.note.slug

        response = self.user_client.post(self.add_url, data=self.form_data)
        self.assertFormError(
            response,
            'form',
            'slug',
            f'{self.note.slug} - {WARNING}'
        )


class TestNoteEditDelete(BaseTestSetUp):
    """Класс теста редактирования и удаления заметки."""

    def test_author_can_delete_note(self):
        """Тест, что автор заметки может ее удалить."""
        before_count = Note.objects.count()
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        after_count = Note.objects.count()
        self.assertEqual(after_count, before_count - 1)

    def test_user_cant_del_note(self):
        """Тест, что читатель не может удалить заметку."""
        before_count = Note.objects.count()
        response = self.user_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        after_count = Note.objects.count()
        self.assertEqual(after_count, before_count)

    def test_author_can_edit_note(self):
        """Тест на редактирование заметки."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.text, self.form_data['text'])
        self.assertEqual(updated_note.author, self.note.author)
        self.assertEqual(updated_note.title, self.form_data['title'])
        self.assertEqual(updated_note.slug, self.form_data['slug'])

    def test_user_cant_edit_comment_of_another_user(self):
        """Тест, что юзер не может редактировать другие заметки."""
        response = self.user_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.text, self.note.text)
        self.assertEqual(updated_note.author, self.note.author)
        self.assertEqual(updated_note.title, self.note.title)
        self.assertEqual(updated_note.slug, self.note.slug)
