import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_anonymous_user_cant_create_comment(client, news, comment_data,
                                            news_detail_url):
    """Проверяем, что анонимный пользователь не может создать комментарий."""
    comments_count_before = Comment.objects.count()
    client.post(news_detail_url, data=comment_data)
    comments_count_after = Comment.objects.count()
    assert comments_count_before == comments_count_after


def test_user_can_create_comment(not_author_client, news, comment_data,
                                 news_detail_url):
    """Проверяем, что авторизованный пользователь может создать комментарий."""
    comments_count_before = Comment.objects.count()
    response = not_author_client.post(news_detail_url, data=comment_data)
    assertRedirects(response, news_detail_url + '#comments')
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before + 1
    comment = Comment.objects.latest('id')
    assert comment.text == comment_data['text']
    assert comment.news == news
    assert comment.author == not_author_client.user


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_user_cant_use_bad_words(author_client, news, bad_word,
                                 news_detail_url):
    """Проверяем, что пользователь не может использовать запрещённые слова."""
    bad_comment_data = {'text': f'Текст, {bad_word}, еще текст'}
    response = author_client.post(news_detail_url, data=bad_comment_data)
    assertFormError(response, 'form', 'text', WARNING)
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(author_client, comment, news_detail_url):
    """Проверяем, что автор может удалить свой комментарий."""
    comments_count_before = Comment.objects.count()
    response = author_client.post(reverse('news:delete', args=(comment.id,)))
    assertRedirects(response, news_detail_url + '#comments')
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before - 1


def test_user_cant_delete_comment_of_another_user(not_author_client, comment):
    """Проверяем, что пользователь не может удалить чужой комментарий."""
    comments_count_before = Comment.objects.count()
    response = not_author_client.post(reverse
                                      ('news:delete', args=(comment.id,)))
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before


def test_author_can_edit_comment(author_client, comment, comment_data,
                                 news_detail_url):
    """Проверяем, что автор может редактировать свой комментарий."""
    comments_count_before = Comment.objects.count()
    response = author_client.post(
        reverse('news:edit', args=(comment.id,)),
        data=comment_data
    )
    assertRedirects(response, news_detail_url + '#comments')
    comment.refresh_from_db()
    assert comment.text == comment_data['text']
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before


def test_user_cant_edit_comment_of_another_user(not_author_client, comment,
                                                comment_data):
    """Проверяем, что пользователь не может редактировать чужой комментарий."""
    comment_before = Comment.objects.get(id=comment.id)
    response = not_author_client.post(
        reverse('news:edit', args=(comment.id,)),
        data=comment_data
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_after = Comment.objects.get(id=comment.id)
    assert comment_before.text == comment_after.text
    assert comment_before.news == comment_after.news
    assert comment_before.author == comment_after.author
