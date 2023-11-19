from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Олеся')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(title='Пишем Unittests',
                                       text='Весь день писала юниттесты',
                                       slug='unittest_writing',
                                       author=cls.author)
        cls.another_author = User.objects.create(username='Данила')
        cls.another_author_client = Client()
        cls.another_author_client.force_login(cls.another_author)

    def test_pages_availability_for_different_users(self):
        data = (
            (self.client, 'notes:home', None, HTTPStatus.OK),
            (self.client, 'users:login', None, HTTPStatus.OK),
            (self.client, 'users:logout', None, HTTPStatus.OK),
            (self.client, 'users:signup', None, HTTPStatus.OK),
            (self.author_client, 'notes:list', None, HTTPStatus.OK),
            (self.author_client, 'notes:add', None, HTTPStatus.OK),
            (self.author_client, 'notes:success', None, HTTPStatus.OK),
            (self.author_client, 'notes:edit', self.note.slug, HTTPStatus.OK),
            (self.author_client, 'notes:delete', self.note.slug,
             HTTPStatus.OK),
            (self.author_client, 'notes:detail', self.note.slug,
             HTTPStatus.OK),
            (self.another_author_client, 'notes:edit', self.note.slug,
             HTTPStatus.NOT_FOUND),
            (self.another_author_client, 'notes:delete', self.note.slug,
             HTTPStatus.NOT_FOUND),
            (self.another_author_client, 'notes:detail', self.note.slug,
             HTTPStatus.NOT_FOUND),

        )
        for client, url, kwargs, response_status in data:
            with self.subTest():
                if kwargs is not None:
                    page_url = reverse(url, kwargs={'slug': kwargs})
                else:
                    page_url = reverse(url)
                response = client.get(page_url)
                self.assertEqual(response.status_code, response_status)

    def test_redirect_to_login_for_anonymous_client(self):
        login_url = reverse('users:login')
        for url in ('notes:edit', 'notes:delete', 'notes:detail',
                    'notes:list', 'notes:add', 'notes:success'):
            with self.subTest():
                if (url == 'notes:list' or url == 'notes:add'
                        or url == 'notes:success'):
                    url = reverse(url)
                else:
                    url = reverse(url, kwargs={'slug': self.note.slug})
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
