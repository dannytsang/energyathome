__author__ = 'Danny Tsang <danny@dannytsang.co.uk>'

import logging
import os


def setup_logging(
    default_path=os.path.dirname(__file__) + os.sep + "energyathome.ini",
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
        _logging = logging.getLogger(__name__)
        _logging.info("Found logging config file: " + path)
    else:
        logging.basicConfig(level=default_level)
        _logging = logging.getLogger(__name__)
        _logging.info("Missing logging config file: " + path)
