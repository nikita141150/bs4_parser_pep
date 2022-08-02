import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import (
    DATETIME_FORMAT,
    BASE_DIR,
    FILE,
    PRETTY
)


def default_output(results, _):
    """
    Вывод данных построчно.
    """
    for row in results:
        print(*row)


def pretty_output(results, _):
    """
    Вывод данных в формате PrettyTable.
    """
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    """
    Создание директории и запись данных в файл csv.
    """
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{now_formatted}.csv'
    file_path = results_dir / file_name

    with open(file_path, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, dialect='unix')
        writer.writerows(results)
    logging.info(f'Файл с результатами был сохранён: {file_path}')


OUTPUTS = {
    PRETTY: (pretty_output),
    FILE: (file_output),
    None: (default_output),
}


def control_output(results, args, outputs=OUTPUTS):
    outputs[args.output](results, args)
