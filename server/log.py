import logging


class CustomFormatter(logging.Formatter):
    grey = "\x1b[90m"
    blue = "\x1b[34m"
    yellow = "\x1b[33m"
    red = "\x1b[31m"
    bold_red = "\x1b[31;1m"
    cyan = "\x1b[36m"
    reset = "\x1b[0m"
    format = "[{}%(levelname)s{}]: %(message)s [{}%(filename)s:%(lineno)d{}]"

    FORMATS = {
        logging.DEBUG: format.format(grey, reset, cyan, reset),
        logging.INFO: format.format(blue, reset, cyan, reset),
        logging.WARNING: format.format(yellow, reset, cyan, reset),
        logging.ERROR: format.format(red, reset, cyan, reset),
        logging.CRITICAL: format.format(bold_red, reset, cyan, reset)
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger('smart-gas-meter-server')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())

logger.addHandler(ch)