from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from .fixtures import BaseTestSetUp

User = get_user_model()


class TestHomePage(BaseTestSetUp):
    """Класс тестов контента."""

    def test_notes_in_list_and_other_users(self):
        """Тест проверки наличия заметок в списке."""
        test_cases = (
            (self.author_client, True),
            (self.user_client, False),
        )
        for client, expected_result in test_cases:
            with self.subTest(client=client, expected_result=expected_result):
                response = client.get(self.list_url)
                self.assertIs(
                    self.note in response.context['object_list'],
                    expected_result,
                    'Заметка '
                    f'{"должна" if expected_result else "не должна"} быть.'
                )

    def test_form_pages(self):
        """Тест формы на страницах добавления и редактирования заметок."""
        test_urls = (
            self.add_url,
            self.edit_url,
        )
        for url in test_urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn(
                    'form',
                    response.context,
                    f'Форма на странице {url} не найдена.'
                )
                self.assertIsInstance(
                    response.context['form'],
                    NoteForm,
                    'Форма не является экземпляром NoteForm.'
                )
