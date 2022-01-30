import os
import sys
import csv
import json
import logging

from firebase import firebase
import plotly.express as px

import config
import utils


class Logger:
    def __init__(self):
        self.logger = self.get_logger()
        self.firebase = firebase.FirebaseApplication(config.FIREBASE_URL, config.FIREBASE_AUTH)
        self.plotly_temperatures = []
        self.local_log = LocalLog()

    def get_logger(self):
        timestamp = utils.get_timestamp()
        filename = config.LOG_NAME_TEMPLATE.format(timestamp)
        file_handler = logging.FileHandler(filename)
        file_handler.setFormatter(config.LOG_FORMAT)

        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(config.LOG_FORMAT)

        logger = logging.getLogger(config.PROJECT_NAME)
        logger.addHandler(file_handler)
        logger.addHandler(stdout_handler)
        logger.setLevel(config.LOG_LEVEL)
        return logger

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def exception(self, message):
        self.logger.exception(message)

    def push_to_firebase(self, event):
        timestamp = utils.get_timestamp()
        data = json.dumps({
            'timestamp': timestamp, 
            'event': event
        })
        self.info(f'Firebase: {data}')
        try:
            self.firebase.post('/events', data)
        except Exception as e:
            self.exception(f'Firebase post failed for data {data}: {e}')

    def push_to_plotly(self, temperature, start=False, end=False):
        timestamp = utils.get_timestamp()
        self.info(f'Plotly: timestamp {timestamp} temperature {temperature}')
        if start:
            self.plotly_temperatures = []
        self.plotly_temperatures.append((timestamp, temperature))
        if not end:
            return
        x_axis = [temperature[0] for temperature in self.plotly_temperatures]
        y_axis = [temperature[1] for temperature in self.plotly_temperatures]
        plot = px.scatter(x=x_axis, y=y_axis)
        try:
            plot.write_html(config.PLOTLY_NAME_TEMPLATE.format(self.plotly_temperatures[0][0]))
        except Exception as e:
            self.exception(f'Could not dump plotly data {self.plotly_temperatures} due to {e}')

    def write_to_local_log(self, temperature, fever_going_on, previous_non_fever):
        timestamp = utils.get_timestamp()
        if temperature >= config.FEVER_LIMIT and not fever_going_on:
            event = config.START_EVENT
        elif fever_going_on and previous_non_fever == config.NON_FEVER_LIMIT:
            event = config.END_EVENT
        else:
            event = config.DEFAULT_EVENT
        data = [timestamp, temperature, event]
        try:
            self.local_log.write_to_local_log(data)
            self.info(f'Wrote to local log: {data}')
        except Exception as e:
            self.exception(f'Failed to write to local log data {timestamp} {temperature} {event} due to {e}')


class LocalLog:
    def __init__(self):
        self.filename = config.LOCAL_LOG_FILENAME
        self.delimiter = config.DELIMITER

    def write_to_local_log(self, data):
        with open(self.filename, 'a') as csv_file:
            writer = csv.writer(csv_file, delimiter=self.delimiter)
            writer.writerow(data)
        
    def get_local_log_rows(self):
        if not os.path.exists(self.filename) or not os.path.isfile(self.filename):
            return []
        with open(self.filename, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=self.delimiter)
            rows = [row for row in csv_reader]
            rows = [row for row in rows[1:] if row]
        return [(int(row[0]), int(row[1]), row[2]) for row in rows]
