import random
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


NEW_COMMENT_TEXT = 'Обновлённый комментарий'


def get_comment_count():
    return Comment.objects.count()


def get_news_detail_url(news):
    return reverse('news:detail', args=(news.id,))


def test_anonymous_user_cant_create_comment(client, news, comment_data):
    initial_comments_count = get_comment_count()
    client.post(
        get_news_detail_url(news),
        data=comment_data
    )
    assert initial_comments_count == get_comment_count()


def test_user_can_create_comment(
    not_author, not_author_client, news, comment_data
):
    initial_comments_count = get_comment_count()
    not_author_client.post(
        get_news_detail_url(news),
        data=comment_data
    )
    assert get_comment_count() == initial_comments_count + 1
    comment = Comment.objects.get(text=comment_data['text'])
    assert comment.text == comment_data['text']
    assert comment.news == news
    assert comment.author == not_author


def test_user_cant_use_bad_words(author_client, news):
    form = author_client.post(
        get_news_detail_url(news),
        data={'text': f'Текст, {random.choice(BAD_WORDS)}, еще текст'}
    ).context['form']
    assert 'text' in form.errors
    assert WARNING in form.errors['text']
    assert get_comment_count() == 0


def test_author_can_delete_comment(author_client, comment, news):
    response = author_client.post(reverse('news:delete', args=(comment.id,)))
    assertRedirects(response, get_news_detail_url(news) + '#comments')
    assert get_comment_count() == 0


def test_user_cant_delete_comment_of_another_user(not_author_client, comment):
    response = not_author_client.post(
        reverse('news:delete', args=(comment.id,))
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert get_comment_count() == 1


def test_author_can_edit_comment(author_client, comment, news, comment_data):
    comment_data['text'] = NEW_COMMENT_TEXT
    assertRedirects(
        author_client.post(
            reverse('news:edit', args=(comment.id,)),
            data=comment_data
        ),
        get_news_detail_url(news) + '#comments'
    )
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT


def test_user_cant_edit_comment_of_another_user(
    not_author_client, comment, news, comment_data
):
    comment_data['text'] = NEW_COMMENT_TEXT
    response = not_author_client.post(
        reverse('news:edit', args=(comment.id,)),
        data=comment_data
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != NEW_COMMENT_TEXT
