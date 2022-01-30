DEBUG = True

# raspberry pi
RASPBERRY_PI_CONNECTED = not DEBUG
SENSOR_TYPE = 11
SENSOR_PIN = 4
RANDOM_GEN_START = 30
RANDOM_GEN_END = 40
READ_RETRY_INTERVAL = 1

# fever events
FEVER_LIMIT = 38.0
START_EVENT = 'FEVER_START_EVENT'
END_EVENT = 'FEVER_END_EVENT'
DEFAULT_EVENT = 'NONE'
NON_FEVER_LIMIT = 10
SAMPLING_TIME = 1

# firebase
FIREBASE_URL = 'https://temperature-monitor-53464.firebaseio.com/'
FIREBASE_AUTH = None

# timing
HOUR_MS = 3600000
DAY_MS = 24 * HOUR_MS

# API
TEMPERATURE_REQUEST = 'temperature'
FEVER_REQUEST = 'fever'
INVALID_ARGS_REQUEST = ['invalid query args', ]
INVALID_TYPE_REQUEST = ['invalid query type', ]

# logger
LOCAL_LOG_FILENAME = 'local_log.csv'
DELIMITER = ','
LOG_NAME_TEMPLATE = 'monitor_log_{}.log'
import logging
LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO
PROJECT_NAME = 'TEMPERATURE MONITOR'
LOG_FORMAT = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# plotly
PLOTLY_NAME_TEMPLATE = 'plot_{}.html'

# web API
PORT = 5051
AGGREGATIONS = ['DAILY', 'HOURLY']
OPERATORS = ['MAX', 'AVERAGE', 'MEDIAN']
HELP_STRINGS = [
    'http://localhost:5051/temperature?start=1588229930147&end=1588229950147',
    'http://localhost:5051/temperature?start={start_date}&end={end_date}&aggregation={aggregation_type}&operator={operator_type}',
    'http://localhost:5051/fever?start={start_date}&end={end_date}', 
    'start_date represents the start timestamp parameter in milliseconds',
    'end_date represents the end timestamp parameter in milliseconds',
    'aggregation_type represents the type of aggregation to be applied on the dataset; it is either HOURLY or DAILY',
    'operator_type represent the type of operation applied on the resolution type specified in aggregation type; it is either AVERAGE, MEDIAN or MAX'
]
HELP_HTML = f'''
    <h1>Temperature Monitor Web API Help</h1>
    <h3>Query Examples</h3>
    <p>
        {HELP_STRINGS[0]}<br/>
        {HELP_STRINGS[1]}</br>
        {HELP_STRINGS[2]}</br>
    </p>
    <h3>Query Arguments</h3>
    <p>
        {HELP_STRINGS[3]}<br/>
        {HELP_STRINGS[4]}</br>
        {HELP_STRINGS[5]}</br>
        {HELP_STRINGS[6]}</br>
    </p>
'''

