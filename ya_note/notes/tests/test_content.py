from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from .test_fixtures import BaseTestSetUp


User = get_user_model()


class TestHomePage(BaseTestSetUp):
    """Класс тестов контента."""

    def test_context_in_list(self):
        """Отдельная заметка попадает на страницу заметок."""
        response = self.author_client.get(self.urls['list'])
        self.assertIn(self.notes, response.context['object_list'])

    def test_other_notes_others_users(self):
        """Чужие заметки не попадают к юзеру."""
        response = self.user_client.get(self.urls['list'])
        self.assertNotIn(self.notes, response.context['object_list'])

    def test_form_pages(self):
        """Тест формы на страницах добавления и редактирования заметок."""
        test_urls = (
            self.urls['add'],
            self.urls['edit'],
        )
        for url in test_urls:
            response = self.author_client.get(url)
            with self.subTest('Проверка наличия формы'):
                self.assertIn(
                    'form',
                    response.context,
                    f'Форма на странице {url} не найдена.'
                )
            with self.subTest('Проверка типа формы.'):
                self.assertIsInstance(
                    response.context['form'],
                    NoteForm,
                    'Форма не является экземпляром NoteForm.'
                )
