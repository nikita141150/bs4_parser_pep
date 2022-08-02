import logging
import re
from collections import defaultdict
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from exceptions import ParserFindTagException
from configs import configure_argument_parser, configure_logging
from constants import (
    BASE_DIR,
    EXPECTED_STATUS,
    MAIN_DOC_URL,
    PEP_URL,
)
from outputs import control_output
from utils import find_tag, get_soup


def whats_new(session):
    """
    Собирает ссылки на статьи о нововведениях в Python,
    забирает информацию об авторах и редакторах статей.
    """
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    sections_by_python = get_soup(
        session, whats_new_url
    ).select_one(
        '#what-s-new-in-python div.toctree-wrapper'
    ).select(
        'li.toctree-l1'
    )
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        try:
            version_link = urljoin(
                whats_new_url, section.find('a')['href']
            )
            soup = get_soup(session, version_link)
            results.append((
                version_link,
                find_tag(soup, 'h1').text,
                find_tag(soup, 'dl').text.replace('\n', ' ')
                ))
        except ConnectionError:
            continue
    return results


def latest_versions(session):
    """
    Собирает информацию о версиях Python.
    """
    ul_tags = get_soup(session, MAIN_DOC_URL).select(
        'div.sphinxsidebarwrapper ul'
    )
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise ValueError('Не найден список c версиями Python')

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append((a_tag['href'], version, status))
    return results


def download(session):
    """
    Скачивает zip архив
    """
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    archive_url = urljoin(
        downloads_url,
        get_soup(
            session, downloads_url
        ).select_one('table.docutils td > a[href$="pdf-a4.zip"]')['href']
    )
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    with open(archive_path, 'wb') as file:
        file.write(session.get(archive_url).content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    """
    Парсер для вывода документов PEP
    """
    tr_tags = get_soup(session, PEP_URL).select('#numerical-index tbody tr')
    pep_statuses_count = defaultdict(int)
    unexpected_vallues = []
    for tr_tag in tqdm(tr_tags):
        td_tags_with_a_tags = find_tag(
            tr_tag, 'td').find_next_sibling('td')
        for td_next_tag in td_tags_with_a_tags:
            link = td_next_tag['href']
            pep_url = urljoin(PEP_URL, link)
            dl_tag = find_tag(
                get_soup(session, pep_url),
                'dl', attrs={'class': 'rfc2822 field-list simple'}
            )
            dd_tag = find_tag(
                dl_tag, 'dt', attrs={'class': 'field-even'}
            ).find_next_sibling('dd')
            status_personal_page = dd_tag.string
            pep_statuses_count[status_personal_page] += 1
            status_pep_general_table = find_tag(
                tr_tag, 'td').string[1:]
            try:
                if status_personal_page not in (
                        EXPECTED_STATUS[status_pep_general_table]):
                    if len(status_pep_general_table) > 2 or (
                            EXPECTED_STATUS[status_pep_general_table] is None):
                        raise KeyError('Получен неожиданный статус')
                    unexpected_vallues.append(
                        f'Несовпадающие статусы:\n {pep_url}\n'
                        f'Cтатус на персональной странице: '
                        f'{status_personal_page}\n'
                        f'Ожидаемые статусы: '
                        f'{EXPECTED_STATUS[status_pep_general_table]}'
                    )
            except ParserFindTagException:
                continue
            else:
                pep_statuses_count[status_personal_page] += 1
    logging.info(unexpected_vallues)
    return [
        ('Статус', 'Количество'),
        *pep_statuses_count.items(),
        ('Total', sum(pep_statuses_count.values())),
    ]


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    """
    Конфигурация парсера аргументов командной строки и
    получение строки нужного режима работы с возможностью логирования.
    """
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    try:
        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()
        results = MODE_TO_FUNCTION[args.mode](session)
        if results is not None:
            control_output(results, args)
    except Exception:
        logging.error('Произошла ошибка', stack_info=True)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
