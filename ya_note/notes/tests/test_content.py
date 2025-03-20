from django.contrib.auth import get_user_model
from .fixtures import BaseTestSetUp

User = get_user_model()


class TestHomePage(BaseTestSetUp):
    """Тесты домашней страницы."""

    def test_context_in_list(self):
        """Проверка наличия заметки в context при доступе к списку."""
        response = self.author_client.get(self.list_url)
        self.assertIn(self.note, response.context['object_list'])

    def test_other_notes_others_users(self):
        """Проверка, что чужие заметки не попадают к пользователю."""
        response = self.user_client.get(self.list_url)
        self.assertNotIn(self.note, response.context['object_list'])
