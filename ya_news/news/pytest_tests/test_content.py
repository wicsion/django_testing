from http import HTTPStatus

from news.forms import CommentForm


def test_news_count(client, create_news, home_url, settings):
    """
    Проверяем, что количество новостей на главной странице
    не превышает установленного лимита.
    """
    response = client.get(home_url)
    assert 'object_list' in response.context, (
        'В контексте ответа отсутствует ключ "object_list".'
    )
    assert (response.context['object_list']
            .count() == settings.NEWS_COUNT_ON_HOME_PAGE), (
        'Количество новостей на странице не соответствует ожидаемому.'
    )


def test_news_order(client, create_news, home_url):
    """
    Проверяем, что новости на главной странице отсортированы
    по дате в порядке убывания.
    """
    response = client.get(home_url)
    assert 'object_list' in response.context, (
        'В контексте ответа отсутствует ключ "object_list".'
    )
    news_list = response.context['object_list']
    sorted_news_list = sorted(news_list, key=lambda x: x.date, reverse=True)
    assert list(news_list) == sorted_news_list, (
        'Новости на главной странице не отсортированы по дате.'
    )


def test_comments_order_on_news_page(client, create_comments, news_detail_url):
    """
    Проверяем, что комментарии на странице новости
    отсортированы по дате в порядке возрастания.
    """
    response = client.get(news_detail_url)
    assert response.status_code == HTTPStatus.OK, (
        'Страница новости не возвращает статус 200.'
    )
    assert 'news' in response.context, (
        'В контексте ответа отсутствует ключ "news".'
    )
    news_comments = response.context['news'].comment_set.all()
    timestamps = [comment.created for comment in news_comments]
    assert timestamps == sorted(timestamps), (
        'Комментарии на странице новости не отсортированы по дате.'
    )


def test_anonymous_client_has_no_form(client, news_detail_url):
    """
    Проверяем, что анонимный пользователь не видит форму
    для добавления комментария.
    """
    response = client.get(news_detail_url)
    assert 'form' not in response.context, (
        'Анонимный пользователь видит форму для добавления комментария.'
    )


def test_authorized_client_has_form(not_author_client, news_detail_url):
    """
    Проверяем, что авторизованный пользователь видит форму
    для добавления комментария.
    """
    response = not_author_client.get(news_detail_url)
    assert 'form' in response.context, (
        'Авторизованный пользователь не видит форму.'
    )
    assert isinstance(response.context['form'], CommentForm), (
        'В контексте ответа форма не является экземпляром CommentForm.'
    )
