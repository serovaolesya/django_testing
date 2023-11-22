import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm

HOME_URL = reverse('news:home')


def test_if_user_has_comment_form(client, admin_client, detail_url):
    non_auth_response = client.get(detail_url)
    auth_response = admin_client.get(detail_url)
    assert isinstance(auth_response.context['form'], CommentForm)
    assert 'form' not in non_auth_response.context


@pytest.mark.django_db
def test_news_count_and_order(client, news_list):
    response = client.get(HOME_URL)
    news_items = response.context['object_list']
    news_count = len(news_items)
    all_dates = [news.date for news in news_items]
    sorted_dates = sorted(all_dates, reverse=True)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, news, comments_list, detail_url):
    response = client.get(detail_url)
    assert 'news' in response.context
    all_comments = list(news.comment_set.all())
    sorted_comments = sorted(all_comments, key=lambda x: x.created)
    assert sorted_comments == all_comments
