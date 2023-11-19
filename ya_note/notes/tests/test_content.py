from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNotesListIsShown(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Олеся')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note_1 = Note.objects.create(title='Тесты на Django',
                                         text='Училась писать тесты...',
                                         slug='learn_to_write_tests',
                                         author=cls.author)
        cls.another_author = User.objects.create(username='Данила')
        cls.another_author_client = Client()
        cls.another_author_client.force_login(cls.another_author)
        cls.note_2 = Note.objects.create(title='Написать ревью кода',
                                         text='Проверить код студента',
                                         slug='write_review',
                                         author=cls.another_author)
        cls.notes_list_url = reverse('notes:list')

    def test_authors_see_only_their_notes_list(self):
        response = self.another_author_client.get(self.notes_list_url)
        self.assertNotContains(response, self.note_1.title)
        self.assertContains(response, self.note_2.title)
        self.assertEqual(len(response.context['object_list']), 1)
        object_list = response.context['object_list']
        self.assertIn(self.note_2, object_list)


class TestNoteFormIsShown(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Олеся')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(title='Тесты на Django',
                                       text='Сегодня училась писать тесты...',
                                       slug='learn_to_write_tests',
                                       author=cls.author)
        cls.add_note_url = reverse('notes:add')
        cls.edit_note_url = reverse('notes:edit',
                                    kwargs={'slug': cls.note.slug})

    def test_auth_user_has_form(self):
        response = self.author_client.get(self.add_note_url)
        self.assertIn('form', response.context)
        response = self.author_client.get(self.edit_note_url)
        self.assertIn('form', response.context)
