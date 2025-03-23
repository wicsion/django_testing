from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.models import Comment
from news.forms import BAD_WORDS, WARNING

pytestmark = pytest.mark.django_db


def test_cant_add_comment_anonymous(client, detail_url,
                                    login_url, form_data):
    """Анонимный пользователь не может отправить комментарий."""
    response = client.post(detail_url, data=form_data)
    expected_redirect = f'{login_url}?next={detail_url}'
    assertRedirects(response, expected_redirect)
    assert Comment.objects.count() == 0


def test_can_add_comment_users(author, author_client,
                               detail_url, form_data, news):
    """Авторизованный пользователь может отправить комментарий."""
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news


def test_bad_words_and_warning_in_comment(not_author_client, detail_url):
    """Комментарий с запрещёнными словами не проходит валидацию."""
    response = not_author_client.post(detail_url, data={'text': BAD_WORDS[0]})
    assert response.status_code == HTTPStatus.OK
    assert Comment.objects.count() == 0
    assertFormError(response, 'form', 'text', WARNING)


def test_users_can_edit_comment(author_client, edit_url,
                                detail_url, form_data, comment):
    """Автор может редактировать свой комментарий."""
    response = author_client.post(edit_url, form_data)
    assertRedirects(response, f'{detail_url}#comments')
    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == form_data['text']
    assert updated_comment.author == comment.author
    assert updated_comment.news == comment.news


def test_users_cant_edit_com(not_author_client,
                             edit_url, comment, form_data):
    """Пользователь не может редактировать чужой комментарий."""
    response = not_author_client.post(edit_url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == comment.text
    assert comment_from_db.author == comment.author
    assert comment_from_db.news == comment.news


def test_users_cant_delete_com(not_author_client,
                               delete_url, comment):
    """Пользователь не может удалить чужой комментарий."""
    response = not_author_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_authors_can_delete_com(author_client, delete_url,
                                detail_url, comment):
    """Автор может удалить свой комментарий."""
    response = author_client.post(delete_url)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == 0
