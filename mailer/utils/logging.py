import logging

logger = logging.getLogger('notification_service_logger')
logger.setLevel('INFO')


def log(msg: str) -> None:
    logger.info(msg)


def error(msg: str) -> None:
    logger.error(msg)
