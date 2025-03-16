import pytest

from notes.forms import NoteForm


@pytest.mark.django_db
class TestFormPage:
    """Тесты отображения форм и списка заметок для разных пользователей."""

    def test_notes_list_for_different_users(
        self, author_client, reader_client, note_author, list_url
    ):
        """Заметка должна отображаться только автору в списке object_list."""
        test_cases = (
            (author_client, True),
            (reader_client, False),
        )
        for client, expected in test_cases:
            with client:
                response = client.get(list_url)
                note_in_list = note_author in response.context['object_list']
                assert note_in_list is expected

    def test_pages_contains_form(self, author_client, add_url, edit_url):
        """На страницах добавления и редактирования отображается форма."""
        for url in (add_url, edit_url):
            response = author_client.get(url)
            assert 'form' in response.context
            assert isinstance(response.context['form'], NoteForm)
