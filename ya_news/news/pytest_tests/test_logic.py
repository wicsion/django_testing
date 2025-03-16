from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, news, comment_data, news_detail_url
):
    """Анонимный пользователь не может создать комментарий."""
    client.post(news_detail_url, data=comment_data)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_can_create_comment(
    not_author, not_author_client, news, comment_data, news_detail_url
):
    """Авторизованный пользователь может создать комментарий."""
    not_author_client.post(news_detail_url, data=comment_data)
    assert Comment.objects.count() == 1
    comment = Comment.objects.first()
    assert comment.text == comment_data['text']
    assert comment.news == news
    assert comment.author == not_author


@pytest.mark.django_db
@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_user_cant_use_bad_words(author_client, news, bad_word):
    """Проверка, что запрещённые слова не допускаются в комментарии."""
    response = author_client.post(
        reverse('news:detail', args=(news.id,)),
        data={'text': f'Текст с запрещённым словом {bad_word}'}
    )
    assertFormError(response, 'form', 'text', WARNING)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment, news):
    """Автор может удалить свой комментарий."""
    response = author_client.post(reverse('news:delete', args=(comment.id,)))
    expected_url = reverse('news:detail', args=(news.id,)) + '#comments'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(not_author_client, comment):
    """Пользователь не может удалить чужой комментарий."""
    response = not_author_client.post(
        reverse('news:delete', args=(comment.id,))
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_author_can_edit_comment(
    author_client, comment, news, comment_data
):
    """Автор может отредактировать свой комментарий."""
    old_author = comment.author
    old_news = comment.news

    response = author_client.post(
        reverse('news:edit', args=(comment.id,)),
        data=comment_data
    )
    expected_url = reverse('news:detail', args=(news.id,)) + '#comments'
    assertRedirects(response, expected_url)

    comment.refresh_from_db()
    assert comment.text == comment_data['text']
    assert comment.author == old_author
    assert comment.news == old_news


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
    not_author_client, comment, comment_data
):
    """Пользователь не может редактировать чужой комментарий."""
    original = Comment.objects.get(id=comment.id)
    comment_data['text'] = 'Попытка редактирования чужого комментария'

    response = not_author_client.post(
        reverse('news:edit', args=(comment.id,)),
        data=comment_data
    )
    assert response.status_code == HTTPStatus.NOT_FOUND

    updated = Comment.objects.get(id=comment.id)
    assert updated.text == original.text
    assert updated.author == original.author
    assert updated.news == original.news
    assert updated.created == original.created
