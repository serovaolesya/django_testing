from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

from django.urls import reverse

HOME_URL = reverse('news:home')
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')
DETAIL_URL = pytest.lazy_fixture('detail_url')
DELETE_URL = pytest.lazy_fixture('delete_url')
EDIT_URL = pytest.lazy_fixture('edit_url')
ADMIN_CLIENT = pytest.lazy_fixture('admin_client')
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    (
        HOME_URL,
        LOGIN_URL,
        LOGOUT_URL,
        SIGNUP_URL,
        DETAIL_URL,
    ),
)
def test_pages_availability_for_anonymous_user(client, name):
    response = client.get(name)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    (
        DELETE_URL,
        EDIT_URL
    ),
)
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (ADMIN_CLIENT, HTTPStatus.NOT_FOUND),
        (AUTHOR_CLIENT, HTTPStatus.OK)
    ),
)
def test_delete_edit_pages_availability_for_users(parametrized_client,
                                                  expected_status,
                                                  name):
    response = parametrized_client.get(name)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    (
        DELETE_URL,
        EDIT_URL
    ),
)
def test_redirects(client, name):
    expected_url = f'{LOGIN_URL}?next={name}'
    response = client.get(name)
    assertRedirects(response, expected_url)
