# Temperature Monitor

Monitor your body temperature and get a record of your past and present fevers.

My first Raspberry Pi related project. Covid-19 inspired.

# Structure

- monitor.py
    - monitors the temperature received from the DHT11 sensor and checks for fever events
    - records data in the local log and in firebase records
    - fever events will be published as a local plotly html

- webapi.py
    'http://localhost:5051/help'
    'http://localhost:5051/temperature?start=1588229930147&end=1588229950147'
    'http://localhost:5051/temperature?start=1588229930147&end=1588229950147&aggregation=HOURLY&operator=MEDIAN'
    'http://localhost:5051/fever?start=1588229930147&end=1588229950147'
    - aggregation: HOURLY, DAILY
    - operator: MAX, AVERAGE, MEDIAN

- local_log.csv
    - headers: timestamp, temperature, event
    - timestamp is epoch time in milliseconds at the time of temperature recording
    - temperature is the received temperature from a DHT11 sensor
    - event can be either of FEVER_START_EVENT, FEVER_END_EVENT or NONE
    - will generate a new log file for each run
