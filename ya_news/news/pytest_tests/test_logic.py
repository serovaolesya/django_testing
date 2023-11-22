import random
from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

COMMENT_TEXT = 'Текст комментария'


def test_user_can_leave_comment(
        author_client, author, form_data, news, detail_url
):
    initial_comments_count = Comment.objects.count()
    response = author_client.post(detail_url, data=form_data)
    expected_url = f'{detail_url}#comments'
    assertRedirects(response, expected_url)
    updated_comments_count = Comment.objects.count()
    assert updated_comments_count == initial_comments_count + 1
    new_comment = Comment.objects.last()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author
    assert new_comment.news == news


@pytest.mark.django_db
def test_anonymous_user_cant_leave_comment(
        client, form_data, news, detail_url
):
    initial_comments_count = Comment.objects.count()
    client.post(detail_url, data=form_data)
    updated_comments_count = Comment.objects.count()
    assert initial_comments_count == updated_comments_count


def test_author_can_edit_comment(
        author, author_client, form_data, news, comment, edit_url, detail_url
):
    initial_comments_count = Comment.objects.count()
    response = author_client.post(edit_url, data=form_data)
    expected_url = f'{detail_url}#comments'
    assertRedirects(response, expected_url)
    comment.refresh_from_db()
    updated_comments_count = Comment.objects.count()
    assert initial_comments_count == updated_comments_count
    assert comment.text == form_data['text']
    assert comment.author == author


def test_another_user_cant_edit_comment(
        admin_client, form_data, comment, edit_url
):
    initial_comments_count = Comment.objects.count()
    response = admin_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    updated_comments_count = Comment.objects.count()
    assert comment.text == COMMENT_TEXT
    assert initial_comments_count == updated_comments_count


def test_author_can_delete_comment(
        author_client, news, comment, delete_url, detail_url
):
    initial_comments_count = Comment.objects.count()
    response = author_client.delete(delete_url)
    expected_url = f'{detail_url}#comments'
    assertRedirects(response, expected_url)
    updated_comments_count = Comment.objects.count()
    assert updated_comments_count == initial_comments_count - 1


def test_another_user_cant_delete_comment(
        admin_client, news, comment, delete_url
):
    initial_comments_count = Comment.objects.count()
    response = admin_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    updated_comments_count = Comment.objects.count()
    assert initial_comments_count == updated_comments_count


def test_user_cant_use_prohibited_words(
        author, author_client, detail_url, news
):
    initial_comments_count = Comment.objects.count()
    initial_author = author
    initial_news = news
    random_bad_word = random.choice(BAD_WORDS)
    bad_words_data = {'text': f'Автор этого поста {random_bad_word}'}
    response = author_client.post(detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    updated_comments_count = Comment.objects.count()
    assert initial_comments_count == updated_comments_count
    comment = Comment.objects.last()
    if comment:
        assert comment.author == initial_author
        assert comment.news == initial_news
