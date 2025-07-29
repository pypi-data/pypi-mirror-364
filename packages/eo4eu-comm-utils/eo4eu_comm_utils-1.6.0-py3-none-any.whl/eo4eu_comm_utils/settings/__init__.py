import logging


logger = logging.getLogger("eo4eu.comm")
logger.setLevel(logging.INFO)


class Settings:
    """Holds library-wide settings"""

    LOGGER = logger
    """The logger used by the library. By default, it's \"eo4eu.comm\""""
