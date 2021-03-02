import logging, os

LOG_LEVELS = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warn': logging.WARNING,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG
}

os.makedirs('logs', exist_ok=True)

logging.basicConfig(level=logging.DEBUG,
                    format='%(name)-3s %(levelname)-8s %(message)s',
                    filename='logs/dut.log', 
                    filemode='w')

console = logging.StreamHandler()
console.setLevel(logging.INFO)

formatter = logging.Formatter('%(message)s')

console.setFormatter(formatter)

logger = logging.getLogger('dut')

logger.addHandler(console)