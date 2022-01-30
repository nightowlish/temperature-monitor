import config
import utils

from logger import LocalLog


class APIHandler:
    def __init__(self, request, request_type):
        self.request = request
        self.request_type = request_type
        self.args = ArgsGetter(self.request)
        self.local_log = LocalLog()

    def get_result(self):
        if not self.validate_args():
            return config.INVALID_ARGS_REQUEST
        if self.request_type == config.FEVER_REQUEST:
            return self.get_fever()
        if self.request_type == config.TEMPERATURE_REQUEST:
            return self.get_temperature()
        return config.INVALID_TYPE_REQUEST

    def validate_args(self):
        try:
            _ = self.args.get_int('start')
            _ = self.args.get_int('end')
        except:
            return False
        if self.args.exists('aggregation'):
            if not self.args.exists('operator'):
                return False
            if not self.args.get('aggregation') in config.AGGREGATIONS:
                return False
        if self.args.exists('operator'):
            if not self.args.exists('aggregation'):
                return False
            if not self.args.get('operator') in config.OPERATORS:
                return False
        return True    

    def get_temperature(self):
        start = self.args.get_int('start')
        end = self.args.get_int('end')
        if self.args.exists('aggregation') and self.args.exists('operator'):
            return self.get_aggregated_temperature(start, end, self.args.get('aggregation'), self.args.get('operator'))
        return self.get_basic_temperature(start, end)

    def get_basic_temperature(self, start, end):
        result = {
            'start_date': start, 
            'end_date': end, 
            'measurements': []
        }
        for row in self.local_log.get_local_log_rows():
            row_time = int(row[0])
            if row_time >= start and row_time <= end:
                result['measurements'].append({
                    'timestamp': row_time, 
                    'value': float(row[1])
                })
        return result

    def get_temperatures_by_duration(self, start, end, duration):
        data = []
        slot_data = []        
        for row in self.local_log.get_local_log_rows():
            row_time = int(row[0])
            if row_time < start or row_time > end:
                continue
            while row_time - start > duration:
                if slot_data:
                    data.append(slot_data)
                    slot_data = []
                start = start + duration
            slot_data.append([row[0], row[1]])
        if slot_data:
            data.append(slot_data)
        return data        

    def get_aggregated_temperature(self, start, end, aggregation, operator):
        duration = config.HOUR_MS if aggregation == 'HOURLY' else config.DAY_MS
        temperatures = self.get_temperatures_by_duration(start, end, duration)
        result = {
            'start_date': start, 
            'end_date': end, 
            'aggregation_type': aggregation, 
            'operator_type': operator, 
            'measurements': []
        }
        for temperature in temperatures:
            temperature_values = [temp[1] for temp in temperature]
            if operator == 'AVERAGE':
                aggregated_value = sum(temperature_values) / len(temperature_values)
            elif operator == 'MEDIAN':
                aggregated_value = utils.median(temperature_values)
            elif operator == 'MAX':
                aggregated_value = max(temperature_values)
            measurement = {
                'timestamp': temperature[0][0], 
                'value': aggregated_value
            }
            result['measurements'].append(measurement)
        return result

    def get_fever(self):
        start = self.args.get_int('start')
        end = self.args.get_int('end')
        result = {
            'start_date': start, 
            'end_date': end, 
            'events': []
        }
        current_event = {}
        event_measurements = []
        for row in self.local_log.get_local_log_rows():
            row_time = int(row[0])
            if row_time < start:
                continue
            if row[2] == config.START_EVENT:
                current_event['event_start'] = row_time
            if not current_event:
                continue
            if row_time <= end:
                event_measurements.append({
                    'timestamp': row_time, 
                    'value': row[1]
                })
            if row[2] == config.END_EVENT:
                current_event['event_end'] = row_time
                current_event['measurements'] = event_measurements
                result['events'].append(current_event)
                current_event = {}
                event_measurements = []
        return result


class ArgsGetter:
    def __init__(self, request):
        self.request = request

    def get_int(self, name):
        return int(self.get(name))

    def get(self, name):
        return self.request.args.get(name)

    def exists(self, name):
        return name in self.request.args
