from requests import RequestException
from bs4 import BeautifulSoup

from exceptions import ParserFindTagException


PAGE_ERROR = 'Возникла ошибка при загрузке страницы {}'


def get_response(session, url):
    """
    Загрузка веб-страницы и
    перехват ошибки RequestException.
    """
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        raise ConnectionError(PAGE_ERROR.format(url))


def find_tag(soup, tag, attrs=None):
    """
    Поиск тегов и перехват ошибки поиска тегов.
    """
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_message = f'Не найден тег {tag} {attrs}'
        raise ParserFindTagException(error_message)
    return searched_tag


def get_soup(session, url):
    return BeautifulSoup(
        get_response(session, url).text, features='lxml'
    )
