from http import HTTPStatus

from django.urls import reverse

from news.forms import CommentForm

NEWS_PER_PAGE = 10


def get_news_detail_url(news):
    return reverse('news:detail', args=(news.id,))


def test_news_count(client, create_news):
    response = client.get(reverse('news:home'))
    assert len(response.context['object_list']) <= NEWS_PER_PAGE
    assert (
        list(response.context['object_list'])
        == list(create_news[:NEWS_PER_PAGE])
    )


def test_comments_order_on_news_page(client, create_comments, news):
    response = client.get(get_news_detail_url(news))
    assert response.status_code == HTTPStatus.OK
    news_comments = response.context['news'].comment_set.all()
    timestamps = [comment.created for comment in news_comments]
    assert timestamps == sorted(timestamps)


def test_anonymous_client_has_no_form(client, news):
    response = client.get(get_news_detail_url(news))
    assert 'form' not in response.context


def test_authorized_client_has_form(not_author_client, news):
    response = not_author_client.get(get_news_detail_url(news))
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
