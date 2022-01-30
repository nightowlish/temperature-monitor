import monitor

from logger import Logger
from monitor import Monitor


def main():
    logger = Logger()
    monitor = Monitor(logger=logger)
    logger.info(f'Starting the monitor...')
    monitor.start_monitoring_temperature()


if __name__ == '__main__':
    main()
