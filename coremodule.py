import time
import csv
import logging
import random                
import json

from firebase import firebase
import plotly.express as px

DATABASE_FILENAME = 'database.csv'
FEVER_LIMIT = 38.0
START_EVENT = 'FEVER_START_EVENT'
END_EVENT = 'FEVER_END_EVENT'
NON_FEVER_LIMIT = 10
SLEEP_DURATION = 30
RASPBERRY_PI_CONNECTED = False
FIREBASE = firebase.FirebaseApplication('https://temperature-monitor-53464.firebaseio.com/', None)

def getTimestamp():
    return int(time.time() * 1000)

def readTemperature():
    if RASPBERRY_PI_CONNECTED:
        import Adafruit_DHT
        humidity, temperature = Adafruit_DHT.read_retry(11, 4)
    else:
        temperature = random.randrange(30, 40)
    logging.info('Temperature reading: {}'.format(temperature))
    return temperature

def pushToFirebase(event):
    timestamp = getTimestamp()
    data = json.dumps({'timestamp': timestamp, 'event': event})
    FIREBASE.post("/events", data)
    logging.info('Firebase: timestamp {} event {}'.format(timestamp, event))

def pushToPlotly(temperature, start=False, end=False):
    timestamp = getTimestamp()
    if start:
        pushToPlotly.temperatures = []
    pushToPlotly.temperatures.append((timestamp, temperature))
    if end:
        plot = px.scatter(x=[temperature[0] for temperature in pushToPlotly.temperatures], y=[temperature[1] for temperature in pushToPlotly.temperatures])
        plot.write_html('plot_{}.html'.format(pushToPlotly.temperatures[0][0]))
    logging.info('Plotly: timestamp {} temperature {}'.format(timestamp, temperature))

def handleFever(temperature):
    logging.info('Handle fever status: fever going on {} previous non fever {} new temperature {}'.format(handleFever.feverGoingOn, handleFever.previousNonFever, temperature))
    if temperature >= FEVER_LIMIT and not handleFever.feverGoingOn:
        pushToFirebase(START_EVENT)
        pushToPlotly(temperature, start=True)            
        handleFever.feverGoingOn = True
        handleFever.previousNonFever = 0
        return

    if handleFever.feverGoingOn and handleFever.previousNonFever == NON_FEVER_LIMIT:
        pushToFirebase(END_EVENT)
        pushToPlotly(temperature, end=True)            
        handleFever.feverGoingOn = False
        handleFever.previousNonFever = 0
        return

    if handleFever.feverGoingOn and temperature < FEVER_LIMIT:
        handleFever.previousNonFever += 1
        logging.info('Increased non fever: {}'.format(handleFever.previousNonFever))
    else:
        logging.info('Reset non fever')
        handleFever.previousNonFever = 0
    
    if handleFever.feverGoingOn:
        pushToPlotly(temperature)            


def writeToDatabase(temperature):
    timestamp = int(time.time() * 1000)
    event = 'NONE'
    if temperature >= FEVER_LIMIT and not handleFever.feverGoingOn:
        event = START_EVENT
    elif handleFever.feverGoingOn and handleFever.previousNonFever == NON_FEVER_LIMIT:
        event = END_EVENT

    with open(DATABASE_FILENAME, 'a') as csvFile:
        writer = csv.writer(csvFile, delimiter=',')
        writer.writerow([timestamp, temperature, event])
        logging.info('Wrote to database: {} {} {}'.format(timestamp, temperature, event))


def startMonitoringTemperature():
    handleFever.feverGoingOn = False
    handleFever.previousNonFever = 0
    while True:
        temperature = readTemperature()
        writeToDatabase(temperature)
        handleFever(temperature)
        time.sleep(SLEEP_DURATION)


def main():
    logging.basicConfig(filename='_log_{}'.format(int(time.time())),level=logging.DEBUG)
    startMonitoringTemperature()

if __name__ == '__main__':
    main()
