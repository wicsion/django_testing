import random

import pytest

from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.models import Comment
from news.forms import WARNING, BAD_WORDS


@pytest.fixture
def news_detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news_detail_url,
                                            comment_data):
    """Анонимный пользователь не может создать комментарий."""
    client.post(news_detail_url, data=comment_data)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_can_create_comment(not_author, not_author_client, news,
                                 comment_data, news_detail_url):
    """Авторизованный пользователь может создать комментарий."""
    not_author_client.post(news_detail_url, data=comment_data)
    assert Comment.objects.count() == 1
    comment = Comment.objects.first()
    assert comment.text == comment_data['text']
    assert comment.news == news
    assert comment.author == not_author


def test_user_cant_use_bad_words(author_client, news):
    form = author_client.post(
        news_detail_url(news),
        data={'text': f'Текст, {random.choice(BAD_WORDS)}, еще текст'}
    ).context['form']
    assert 'text' in form.errors
    assert WARNING in form.errors['text']
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, delete_url, news_detail_url):
    """Автор может удалить свой комментарий."""
    response = author_client.post(delete_url)
    assertRedirects(response, news_detail_url + '#comments')
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(not_author_client,
                                                  delete_url):
    """Пользователь не может удалить чужой комментарий."""
    response = not_author_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, comment,
                                 edit_url, comment_data, news_detail_url):
    """Автор может отредактировать свой комментарий."""
    original_news = comment.news
    original_author = comment.author

    new_text = 'Обновлённый текст комментария'
    comment_data['text'] = new_text

    response = author_client.post(edit_url, data=comment_data)
    assertRedirects(response, news_detail_url + '#comments')

    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == new_text
    assert updated_comment.news == original_news
    assert updated_comment.author == original_author


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(not_author_client, comment,
                                                edit_url, comment_data):
    """Пользователь не может редактировать чужой комментарий."""
    original = Comment.objects.get(id=comment.id)
    comment_data['text'] = 'Попытка взлома'

    response = not_author_client.post(edit_url, data=comment_data)
    assert response.status_code == HTTPStatus.NOT_FOUND

    updated = Comment.objects.get(id=comment.id)
    assert updated.text == original.text
    assert updated.news == original.news
    assert updated.author == original.author
