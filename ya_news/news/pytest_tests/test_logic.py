from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

COMMENT_TEXT = 'Текст комментария'


def test_user_can_leave_comment(
        author_client, author, form_data, news, news_pk
):
    url = reverse('news:detail', args=news_pk)
    response = author_client.post(url, data=form_data)
    expected_url = f'{url}#comments'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author
    assert new_comment.news == news


@pytest.mark.django_db
def test_anonymous_user_cant_leave_comment(client, form_data, news, news_pk):
    url = reverse('news:detail', args=news_pk)
    client.post(url, data=form_data)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
        author, author_client, form_data, news_pk, comment, comment_pk
):
    url = reverse('news:edit', args=comment_pk)
    response = author_client.post(url, data=form_data)
    detail_url = reverse('news:detail', args=news_pk)
    expected_url = f'{detail_url}#comments'
    assertRedirects(response, expected_url)
    comment.refresh_from_db()
    comments_count = Comment.objects.count()
    assert comments_count == 1
    assert comment.text == form_data['text']
    assert comment.author == author


def test_another_user_cant_edit_comment(
        admin_client, form_data, comment, comment_pk
):
    url = reverse('news:edit', args=comment_pk)
    response = admin_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT


def test_author_can_delete_comment(
        author_client, news_pk, comment, comment_pk
):
    url = reverse('news:delete', args=comment_pk)
    response = author_client.delete(url)
    detail_url = reverse('news:detail', args=news_pk)
    expected_url = f'{detail_url}#comments'
    assertRedirects(response, expected_url)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_another_user_cant_delete_comment(
        admin_client, news_pk, comment, comment_pk
):
    url = reverse('news:delete', args=comment_pk)
    response = admin_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_user_cant_use_prohibited_words(
        author, author_client, news_pk
):
    url = reverse('news:detail', args=news_pk)
    bad_words_data = {'text': f'Автор этого поста {BAD_WORDS[0]}'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0
