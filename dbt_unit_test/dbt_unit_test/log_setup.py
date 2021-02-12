import logging

LOG_LEVELS = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warn': logging.WARNING,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG
}

logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='logs/dut.log', 
                    filemode='w')

console = logging.StreamHandler()
console.setLevel(logging.INFO)

formatter = logging.Formatter('%(name)s: %(message)s')

console.setFormatter(formatter)

logging.getLogger('').addHandler(console)

logger = logging.getLogger('dut')