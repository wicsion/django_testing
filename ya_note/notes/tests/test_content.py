from django.contrib.auth import get_user_model
from notes.forms import NoteForm
from .test_fixtures import BaseTestSetUp

User = get_user_model()


class TestHomePage(BaseTestSetUp):
    """Класс тестов контента."""

    def test_context_in_list(self):
        """Отдельная заметка передаётся на страницу со списком заметок."""
        test_data = (
            (self.author_client, True),
            (self.user_client, False),
        )

        for client, expected in test_data:
            with self.subTest(client=client):
                response = client.get(self.urls['list'])
                note_in_list = self.notes in response.context['object_list']
                self.assertIs(note_in_list, expected)

    def test_form_pages(self):
        """Тест формы на страницах добавления и редактирования заметок."""
        test_urls = (
            self.urls['add'],
            self.urls['edit'],
        )

        for url in test_urls:
            response = self.author_client.get(url)
            with self.subTest(url=url, check='Проверка наличия формы'):
                self.assertIn(
                    'form',
                    response.context,
                    f'Форма на странице {url} не найдена.'
                )
            with self.subTest(url=url, check='Проверка типа формы'):
                self.assertIsInstance(
                    response.context['form'],
                    NoteForm,
                    f'Форма  {url} не является экземпляром NoteForm.'
                )
