__author__ = 'Danny Tsang <danny@dannytsang.co.uk>'

import logging, os


def setup_logging(
    default_path='energyathome.ini',
    default_level=logging.DEBUG,
    env_key='LOG_CFG'
):
    """Setup logging configuration

    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        logging.config.fileConfig(path)
    else:
        logging.basicConfig(level=default_level)
