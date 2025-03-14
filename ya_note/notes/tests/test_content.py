from django.contrib.auth import get_user_model

from notes.forms import NoteForm


User = get_user_model()


class TestFormPage:
    """Тестирование страниц с формами для заметок."""

    def test_notes_list_for_different_users(self, author_client, reader_client,
                                            note_author, notes_list_url):
        """Проверяем, что заметки отображаются только для их авторов."""
        test_cases = [
            (author_client, True),
            (reader_client, False),
        ]

        for client, expected_result in test_cases:
            with self.subTest(client=client, expected_result=expected_result):
                response = client.get(notes_list_url)
                object_list = response.context['object_list']
                self.assertIs(
                    note_author in object_list, expected_result,
                    f'Заметка автора '
                    f'{"должна" if expected_result else "не должна"} '
                    'быть в списке.'
                )

    def test_pages_contains_form(self, author_client, note_author,
                                 add_note_url, edit_note_url):
        """Проверяем, что на страницах присутствует форма."""
        form_urls = [
            (add_note_url, None),
            (edit_note_url, (note_author.slug,)),
        ]

        for url, args in form_urls:
            with self.subTest(url=url):
                response = author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
