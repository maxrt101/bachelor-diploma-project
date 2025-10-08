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


logger = logging.getLogger('smart-gas-meter-rpi')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())

logger.addHandler(ch)


if __name__ == '__main__':
    print('[\x1b[34mINFO\x1b[0m]: Start capturing [\x1b[36mapp.py:151\x1b[0m]')
    print('[\x1b[34mINFO\x1b[0m]: Capture: captures/capture_28-05-2024_12-01-27.jpg [\x1b[36mapp.py:54\x1b[0m]')
    print('Results saved to \x1b[1mruns/detect/predict29\x1b[0m')
    for x, c, p in [
        (109, 0, 78),
        (139, 0, 78),
        (170, 0, 79),
        (200, 0, 81),
        (230, 0, 85),
        (264, 1, 71),
        (296, 0, 88),
        (326, 6, 95)
    ]:
        print(f'[\x1b[90mDEBUG\x1b[0m]: Detect: x={x} cls={c} conf={round(p/100, 2)} [\x1b[36mdetect.py:61\x1b[0m]')
    print('[\x1b[34mINFO\x1b[0m]: Scan result: 00000106 [\x1b[36mapp.py:64\x1b[0m]')
    print('[\x1b[34mINFO\x1b[0m]: Send readings: "00000106" (28-05-2024_12-01-27) [\x1b[36mapp.py:68\x1b[0m]')
