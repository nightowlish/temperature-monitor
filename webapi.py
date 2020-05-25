# def getDatabaseRows

import flask
import csv

from flask import request, jsonify

DATABASE_FILENAME = 'database.csv'
HOUR_MS = 3600000
DAY_MS = 24 * HOUR_MS
INVALID_QUERY = ['invalid query args', ]
START_EVENT = 'FEVER_START_EVENT'
END_EVENT = 'FEVER_END_EVENT'

app = flask.Flask(__name__)
app.config['DEBUG'] = True


def median(values):
    n = len(values)
    s = sorted(values)
    return (sum(s[n//2-1:n//2+1])/2.0, s[n//2])[n % 2] if n else None

def getDatabaseRows():
    with open(DATABASE_FILENAME, 'r') as csvFile:
        csvReader = csv.reader(csvFile, delimiter=',')
        rows = [row for row in csvReader]
        rows = [row for row in rows[1:] if row]
        return [(int(row[0]), int(row[1]), row[2]) for row in rows]

def getFever(request):
    start = int(request.args.get('start'))
    end = int(request.args.get('end'))
    result = {'start_date': start, 'end_date': end, 'events': []}
    currentEvent = {}
    eventMeasurements = []
    for row in getDatabaseRows():
        rowTime = int(row[0])
        if rowTime < start:
            continue
        if row[2] == START_EVENT:
            currentEvent['event_start'] = rowTime
        if currentEvent:
            if rowTime <= end:
                eventMeasurements.append({'timestamp': rowTime, 'value': row[1]})
            if row[2] == END_EVENT:
                currentEvent['event_end'] = rowTime
                currentEvent['measurements'] = eventMeasurements
                result['events'].append(currentEvent)
                currentEvent = {}
                eventMeasurements = {}
    return result

def getTemperaturesByDuration(start, end, duration):
    data = []
    slotData = []        
    for row in getDatabaseRows():
        rowTime = int(row[0])
        if rowTime < start or rowTime > end:
            continue
        while rowTime - start > duration:
            if slotData:
                data.append(slotData)
                slotData = []
            start = start + duration
        slotData.append([row[0], row[1]])
    if slotData:
        data.append(slotData)
    return data        

def getAggregatedTemperature(start, end, aggregation, operator):
    duration = HOUR_MS if aggregation == 'HOURLY' else DAY_MS
    temperatures = getTemperaturesByDuration(start, end, duration)
    result = {'start_date': start, 'end_date': end, 'aggregation_type': aggregation, 'operator_type': operator, 'measurements': []}
    for temperature in temperatures:
        temperatureValues = [temp[1] for temp in temperature]
        print(temperatureValues)
        if operator == 'AVERAGE':
            aggregatedValue = sum(temperatureValues) / len(temperatureValues)
        elif operator == 'MEDIAN':
            aggregatedValue = median(temperatureValues)
        elif operator == 'MAX':
            aggregatedValue = max(temperatureValues)
        measurement = {'timestamp': temperature[0][0], 'value': aggregatedValue}
        result['measurements'].append(measurement)
    return result

def getBasicTemperature(start, end):
    result = {'start_date': start, 'end_date': end, 'measurements': []}
    for row in getDatabaseRows():
        rowTime = int(row[0])
        if rowTime >= start and rowTime <= end:
            result['measurements'].append({'timestamp': rowTime, 'value': float(row[1])})
    return result

def getTemperature(request):
    start = int(request.args.get('start'))
    end = int(request.args.get('end'))
    if 'aggregation' in request.args and 'operator' in request.args:
        return getAggregatedTemperature(start, end, request.args.get('aggregation'), request.args.get('operator'))
    return getBasicTemperature(start, end)

def checkArgs(request):
    if not 'start' in request.args or not 'end' in request.args:
        return False
    try:
        start = int(request.args.get('start'))
        start = int(request.args.get('end'))
    except:
        return False
    if 'aggregation' in request.args:
        if not 'operator' in request.args:
            return False
        aggregation = request.args.get('aggregation')
        if not aggregation == 'HOURLY' and not aggregation == 'DAILY':
            return False
    if 'operator' in request.args:
        if not 'aggregation' in request.args:
            return False
        operator = request.args.get('operator')
        if not operator == 'AVERAGE' and not operator == 'MEDIAN' and not operator == 'MAX':
            return False
    return True    

@app.route('/<requestType>', methods=['GET'])
def getRequest(requestType):  
    if not checkArgs(request):
        result = INVALID_QUERY
    elif requestType == 'fever':
        result = getFever(request)
    elif requestType == 'temperature':
        result = getTemperature(request)
    else:
        result = ['invalid query type', ]
    return jsonify(result)

@app.route('/help', methods=['GET'])
def _help():
    helpStrings = [
        'http://localhost:5051/temperature?start=1588229930147&end=1588229950147',
        'http://localhost:5051/temperature?start={start_date}&end={end_date}&aggregation={aggregation_type}&operator={operator_type}',
        'http://localhost:5051/fever?start={start_date}&end={end_date}', 
        'start_date represents the start timestamp parameter in milliseconds',
        'end_date represents the end timestamp parameter in milliseconds',
        'aggregation_type represents the type of aggregation to be applied on the dataset; it is either HOURLY or DAILY',
        'operator_type represent the type of operation applied on the resolution type specified in aggregation type; it is either AVERAGE, MEDIAN or MAX'
    ]
    helpHtml = '''
    <h1>Temperature Monitor Web API Help</h1>
    <h3>Query Examples</h3>
    <p>{}<br/>{}</br>{}</br></p>
    <h3>Query Arguments</h3>
    <p>{}<br/>{}</br>{}</br>{}</br></p>
    '''.format(helpStrings[0], helpStrings[1], helpStrings[2], helpStrings[3], helpStrings[4], helpStrings[5], helpStrings[6])
    return helpHtml

def main():
    app.run(port=5051)

if __name__ == '__main__':
    main()
