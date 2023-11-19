import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


def test_if_user_has_comment_form(client, admin_client, news_pk):
    url = reverse('news:detail', args=news_pk)
    non_auth_response = client.get(url)
    auth_response = admin_client.get(url)
    assert isinstance(auth_response.context['form'], CommentForm)
    assert 'form' not in non_auth_response.context


@pytest.mark.django_db
def test_news_count_and_order(client, news_list):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, news, news_pk, comments_list):
    url = reverse('news:detail', args=news_pk)
    response = client.get(url)
    assert 'news' in response.context
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created
