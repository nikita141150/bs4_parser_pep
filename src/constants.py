from pathlib import Path

MAIN_DOC_URL = 'https://docs.python.org/3/'
PEP_URL = 'https://peps.python.org/'


BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = LOG_DIR / 'parser.log'
DOWNLOADS_DIR = BASE_DIR / 'downloads'
RESULTS_DIR = BASE_DIR / 'results'

EXPECTED_STATUS = {
    'A': ['Active', 'Accepted'],
    'D': ['Deferred'],
    'F': ['Final'],
    'P': ['Provisional'],
    'R': ['Rejected'],
    'S': ['Superseded'],
    'W': ['Withdrawn'],
    '': ['Draft', 'Active'],
}

LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'


PRETTY = 'pretty'
FILE = 'file'
