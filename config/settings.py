import logging
from pathlib import Path
import yaml

default_file = Path(__file__).parent / 'config.yaml'

with open(default_file, 'r') as file:
    config = yaml.safe_load(file)

telegram_bot = config.get('telegram_bot')
torrents_cfg = config.get('torrents')
favourites = config.get('favourites')
auth_cfg = config.get('auth_cfg')

LOG_LEVEL_MAP = {
    'CRITICAL': logging.CRITICAL,
    'FATAL': logging.FATAL,
    'ERROR': logging.ERROR,
    'WARN': logging.WARNING,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    'NOTSET': logging.NOTSET,
}

LOG_LEVEL = LOG_LEVEL_MAP.get(config.get('log_level', 'INFO'), logging.INFO)
