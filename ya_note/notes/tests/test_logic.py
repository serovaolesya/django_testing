from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytest_django.asserts import assertFormError
from pytils.translit import slugify


from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Олеся')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.add_note_url = reverse('notes:add')
        cls.form_data = {
            'title': 'Заголовок', 'text': 'Текст', 'slug': 'new_note'
        }
        cls.redirect_url = reverse('notes:success')

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.add_note_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_auth_user_can_create_note(self):
        response = self.author_client.post(self.add_note_url,
                                           data=self.form_data)
        self.assertRedirects(response, self.redirect_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)


class TestEditDeleteSlug(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Олеся')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note_1 = Note.objects.create(
            title='Тесты на Django',
            text='Сегодня училась писать тесты...',
            slug='learn_to_write_tests',
            author=cls.author
        )
        cls.another_author = User.objects.create(username='Данила')
        cls.another_author_client = Client()
        cls.another_author_client.force_login(cls.another_author)
        cls.delete_note_url = reverse('notes:delete', kwargs={
            'slug': cls.note_1.slug}
        )
        cls.edit_note_url = reverse('notes:edit', kwargs={
            'slug': cls.note_1.slug}
        )
        cls.add_note_url = reverse('notes:add')
        cls.redirect_url = reverse('notes:success')

        cls.form_data = {
            'title': 'Тесты на Django',
            'text': 'Тесты, вроде бы, написаны...',
            'slug': 'learn_to_write_tests'
        }

    def test_author_can_delete_their_note(self):
        response = self.author_client.delete(self.delete_note_url)
        self.assertRedirects(response, self.redirect_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_author_can_edit_their_note(self):
        response = self.author_client.post(self.edit_note_url,
                                           data=self.form_data)
        self.assertRedirects(response, self.redirect_url)
        self.note_1.refresh_from_db()
        self.assertEqual(self.note_1.text, self.form_data['text'])

    def test_non_author_cant_delete_note_of_another_user(self):
        response = self.another_author_client.delete(self.delete_note_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_non_author_cant_edit_note_of_another_user(self):
        response = self.another_author_client.post(self.edit_note_url,
                                                   data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note_1.refresh_from_db()
        self.assertNotEqual(self.note_1.text, self.form_data['text'])

    def test_slug_is_not_unique(self):
        response = self.author_client.post(self.add_note_url,
                                           data=self.form_data)
        assertFormError(
            response, 'form', 'slug', errors=(self.note_1.slug + WARNING)
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_slug_autofill_when_empty(self):
        self.form_data.pop('slug')
        response = self.author_client.post(self.add_note_url,
                                           data=self.form_data)
        self.assertRedirects(response, self.redirect_url)
        assert Note.objects.count() == 2
        note_2 = Note.objects.get(pk=2)
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(note_2.slug, expected_slug)
