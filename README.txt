
Structure:

    - database.csv  - a CSV file with headers timestamp,temperature,event
        - timestamp is epoch time in milliseconds at the time of temperature recording
        - temperature is the received temperature from module 
            - can be either from a DHT11 sensor or a randomly generated value between 30 and 40 - values chosen for a more probable ease in testing events
        - event can be either of FEVER_START_EVENT, FEVER_END_EVENT or NONE
        - will generate a new log file for each run

    - coremodule.py - responsible for receiving temperature, keeping track of fever events, recording data in csv, firebase records and plotly records
        - constants: 
            SLEEP_DURATION - duration between temperature reads
            FEVER_LIMIT - minimum temperature considered to be a fever, 
            RASPBERRY_PI_CONNECTED - whether a raspberry pi with a dht11 sensor is connected for temperature reads; if False, temperatures will be generated randomly
        - temperatures recorded between FEVER_START_EVENT and FEVER_END_EVENT will be published as a local plotly html after the last read of the event
        - events will be pushed to firebase
        
    - webapi - implemented as in requirements; possible types of requests:
        'http://localhost:5051/help'
        'http://localhost:5051/temperature?start=1588229930147&end=1588229950147'
        'http://localhost:5051/temperature?start=1588229930147&end=1588229950147&aggregation=HOURLY&operator=MEDIAN'
        'http://localhost:5051/fever?start=1588229930147&end=1588229950147' 
        - aggregation: HOURLY, DAILY
        - operator: MAX, AVERAGE, MEDIAN
        

        