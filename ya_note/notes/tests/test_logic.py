from http import HTTPStatus

from django.contrib.auth import get_user_model

from notes.models import Note
from .test_fixtures import BaseTestSetUp

User = get_user_model()


class TestNoteCreate(BaseTestSetUp):
    """Класс теста заметки."""

    def test_anonymous_note(self):
        """Тест, аноним не может создать заметку."""
        before_count = Note.objects.count()
        self.client.post(self.urls['add'], data=self.form_data)
        after_count = Note.objects.count()
        self.assertEqual(before_count, after_count)

    def test_user_can_create_notes(self):
        """Тест, что юзер может создать заметку."""
        Note.objects.all().delete()
        response = self.user_client.post(self.urls['add'], data=self.form_data)
        self.assertRedirects(response, self.urls['success'])
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.author, self.user)
        self.assertEqual(note.title, self.form_data['title'])


class TestNoteEditDelete(BaseTestSetUp):
    """Класс теста редактирования заметки."""

    NOTE_TEXT = 'Текст комментария'
    NEW_NOTE_TEXT = 'Обновлённый комментарий'

    def test_author_can_delete_note(self):
        """Тест, что автор заметки может ее удалить."""
        before_count = Note.objects.count()
        response = self.author_client.delete(self.urls['delete'])
        self.assertRedirects(response, self.urls['success'])
        after_count = Note.objects.count()
        self.assertEqual(after_count, before_count - 1)

    def test_user_cant_del_note(self):
        """тест, что читатель не может удалить заметку."""
        before_count = Note.objects.count()
        response = self.user_client.delete(self.urls['delete'])
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        after_count = Note.objects.count()
        self.assertEqual(after_count, before_count)

    def test_author_can_edit_note(self):
        """тест на редактирование заметки."""
        note_id = self.notes.id
        self.form_data['text'] = self.NEW_NOTE_TEXT
        response = self.author_client.post(
            self.urls['edit'], data=self.form_data
        )
        updated_note = Note.objects.get(id=note_id)
        self.assertRedirects(response, self.urls['success'])
        self.assertEqual(updated_note.text, self.form_data['text'])
        self.assertEqual(updated_note.author, self.notes.author)
        self.assertEqual(updated_note.title, self.form_data['title'])

    def test_user_cant_edit_comment_of_another_user(self):
        """Тест, что юзер не может редактировать другие заметки."""
        note_id = self.notes.id
        response = self.user_client.post(
            self.urls['edit'], data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        updated_note = Note.objects.get(id=note_id)
        self.assertEqual(updated_note.text, self.notes.text)
        self.assertEqual(updated_note.author, self.notes.author)
        self.assertEqual(updated_note.title, self.notes.title)
        self.assertEqual(updated_note.slug, self.notes.slug)
