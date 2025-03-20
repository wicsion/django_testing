from django.contrib.auth import get_user_model
from notes.forms import NoteForm
from .fixtures import BaseTestSetUp

User = get_user_model()


class TestHomePage(BaseTestSetUp):
    """Класс тестов контента."""

    def test_notes_in_object_list(self):
        """Проверка отображения заметок в списке у нужного пользователя."""
        test_cases = (
            (self.author_client, True),
            (self.user_client, False),
        )
        for client, expected in test_cases:
            response = client.get(self.urls['list'])
            with self.subTest(client=client):
                object_list = response.context['object_list']
                self.assertIs(self.notes in object_list, expected)

    def test_form_pages(self):
        """Тест формы на страницах добавления и редактирования заметок."""
        test_urls = (self.urls['add'], self.urls['edit'])
        with self.subTest('Проверка форм на страницах'):
            for url in test_urls:
                response = self.author_client.get(url)
                self.assertIn(
                    'form',
                    response.context,
                    f'Форма на странице {url} не найдена.'
                )
                self.assertIsInstance(
                    response.context['form'],
                    NoteForm,
                    f'Форма  {url} не является экземпляром NoteForm.'
                )
