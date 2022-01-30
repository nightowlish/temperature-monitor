import time
import logging
import random                

import config


class Monitor:
    def __init__(self, logger=None):
        self.logger = logging if logger is None else logger
        self.fever_going_on = False
        self.previous_non_fever = 0
        
    def start_monitoring_temperature(self):
        while True:
            temperature = self.read_temperature()
            self.logger.write_to_local_log(temperature, self.fever_going_on, self.previous_non_fever)
            self.handle_fever(temperature)
            time.sleep(config.SAMPLING_TIME)

    def read_temperature(self):
        if config.RASPBERRY_PI_CONNECTED:
            import Adafruit_DHT
            while True:
                try:
                    __humidity, temperature = Adafruit_DHT.read_retry(config.SENSOR_TYPE, config.SENSOR_PIN)
                    break
                except Exception as e:
                    self.logger.exception(f'Could not get sensor readings: {e}. Will retry in {config.READ_RETRY_INTERVAL} seconds.')
                    time.sleep(config.READ_RETRY_INTERVAL)
        else:
            temperature = random.randrange(config.RANDOM_GEN_START, config.RANDOM_GEN_END)
        self.logger.info(f'Temperature reading: {temperature}')
        return temperature

    def handle_fever(self, temperature):
        self.logger.info(f'Handle fever pre-status: fever going on: {self.fever_going_on}, previous non fever: {self.previous_non_fever}, new temperature: {temperature}')
        if temperature >= config.FEVER_LIMIT and not self.fever_going_on:
            self.handle_fever_start(temperature)
        elif self.fever_going_on and self.previous_non_fever == config.NON_FEVER_LIMIT:
            self.handle_fever_end(temperature)
        else:
            self.handle_normal_reading(temperature)
        self.logger.info(f'Handle fever post-status: fever going on: {self.fever_going_on}, previous non fever: {self.previous_non_fever}, new temperature: {temperature}')

    def handle_fever_start(self, temperature):
        self.logger.push_to_firebase(config.START_EVENT)
        self.logger.push_to_plotly(temperature, start=True)            
        self.fever_going_on = True
        self.previous_non_fever = 0

    def handle_fever_end(self, temperature):
        self.logger.push_to_firebase(config.END_EVENT)
        self.logger.push_to_plotly(temperature, end=True)            
        self.fever_going_on = False
        self.previous_non_fever = 0

    def handle_normal_reading(self, temperature):
        if self.fever_going_on and temperature < config.FEVER_LIMIT:
            self.previous_non_fever += 1
            self.logger.info(f'Increased non fever: {self.previous_non_fever}')
        else:
            logging.info(f'Reset non fever')
            self.previous_non_fever = 0
        if self.fever_going_on:
            self.logger.push_to_plotly(temperature)            
