from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note
from notes.tests.test_routes import TestFixtures


User = get_user_model()

NOTE_DATA = {
    'title': 'Новая заметка',
    'text': 'Новый текст'
}


class TestLogic(TestFixtures):

    def test_not_unique_slug(self):
        self.client.force_login(self.author)
        new_note = {
            'title': 'Заметка автора',
            'text': 'Новый текст'
        }
        slug = slugify('Заметка автора')
        self.assertFormError(
            self.client.post(reverse('notes:add'), data=new_note),
            'form',
            'slug',
            errors=(
                f'{slug} - такой slug уже существует, '
                'придумайте уникальное значение!'
            )
        )

    def test_slug_automatic_generation(self):
        self.assertEqual(
            self.note_author.slug,
            slugify(self.note_author.title)
        )

    def test_note_creation_with_author(self):
        self.client.force_login(self.reader)
        self.client.post(reverse('notes:add'), NOTE_DATA)
        self.assertEqual(Note.objects.count(), 3)
        new_note = Note.objects.get(title='Новая заметка')
        self.assertEqual(new_note.author, self.reader)

    def test_anonymous_user_cant_create_note(self):
        self.client.post(reverse('notes:add'), NOTE_DATA)
        self.assertEqual(Note.objects.count(), 2)

    def test_user_permissions_for_editing_and_deleting_notes(self):
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
                    url = reverse(
                        'notes:delete',
                        args=(self.note_author.slug,)
                    )
                elif action == 'edit':
                    url = reverse('notes:edit', args=(self.note_author.slug,))

                self.assertEqual(
                    self.client.post(url).status_code,
                    expected_status
                )
