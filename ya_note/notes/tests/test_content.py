from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.tests.test_routes import TestFixtures
from notes.forms import NoteForm


User = get_user_model()


class TestFormPage(TestFixtures):

    def test_notes_list_for_different_users(self):
        self.client.force_login(self.author)
        response = self.client.get(reverse('notes:list'))
        self.assertIn(self.note_author, response.context['object_list'])
        self.assertContains(response, self.note_author.title)
        self.assertNotContains(response, self.note_reader.title)
        self.client.force_login(self.reader)
        response = self.client.get(reverse('notes:list'))
        self.assertIn(self.note_reader, response.context['object_list'])
        self.assertContains(response, self.note_reader.title)
        self.assertNotContains(response, self.note_author.title)

    def test_pages_contains_form(self):
        self.client.force_login(self.author)
        form_urls = (
            ('notes:add', ()),
            ('notes:edit', (self.note_author.slug,))
        )
        for name, args in form_urls:
            with self.subTest(name=name):
                response = self.client.get(reverse(name, args=args))
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
