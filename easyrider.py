import json
import re


def print_results(results):
    print(f'Type and required field validation: {sum(results.values())} errors')
    for error in results:
        print(f'{error}: {results[error]}')


def check_data(file):
    chars = ['', 'S', 'O', 'F']

    result = {'bus_id': 0, 'stop_id': 0, 'stop_name': 0, 'next_stop': 0, 'stop_type': 0, 'a_time': 0}
    for record in file:
        if not record['bus_id'] or not isinstance(record['bus_id'], int):
            result['bus_id'] += 1

        if not record['stop_id'] or not isinstance(record['stop_id'], int):
            result['stop_id'] += 1

        if not record['stop_name'] or not isinstance(record['stop_name'], str):
            result['stop_name'] += 1

        if not isinstance(record['next_stop'], int):
            result['next_stop'] += 1

        if not record['stop_type'] in chars:
            result['stop_type'] += 1

        if not record['a_time'] or not isinstance(record['a_time'], str):
            result['a_time'] += 1
        else:
            if record['a_time'].count(':'):
                time = record['a_time'].split(':')
                if len(time) == 2 and 0 <= int(time[0]) < 24 and 0 <= int(time[1]) < 60:
                    continue
                else:
                    result['a_time'] += 1
            else:
                result['a_time'] += 1
    print_results(result)


def check_syntax(file):
    result = {'stop_name': 0, 'stop_type': 0, 'a_time': 0}
    stop_nams = {'Road', 'Avenue', 'Boulevard', 'Street'}
    stop_types = {'S', 'O', 'F'}

    for record in file:
        stop_nam = re.match(r'([A-Z]\w+ )+([A-Z]\w+)', record['stop_name'])
        if not stop_nam or not stop_nam.group(2) in stop_nams:
            result['stop_name'] += 1
        if record['stop_type'] and not record['stop_type'] in stop_types:
            result['stop_type'] += 1
        if not re.match(r'([0-1]\d|2[0-3]):[0-5]\d$', record['a_time']):
            result['a_time'] += 1

    print_results(result)


def check_line(file):
    result = {}
    for record in file:
        if record['bus_id'] in result.keys():
            result[record['bus_id']] += 1
        else:
            result[record['bus_id']] = 1

    print('Line names and number of stops:')
    for bus in result:
        print(f'bus_id: {bus}, stops: {result[bus]}')


def check_special(file):
    result = {}
    stops = {}
    start_stops = []
    finish_stops = []
    for record in file:
        if record['bus_id'] in result.keys() and record['stop_type']:
            result[record['bus_id']].append(record['stop_type'])
        elif record['stop_type']:
            result[record['bus_id']] = list(record['stop_type'])

        if record['stop_type'] == 'S' and not record['stop_name'] in start_stops:
            start_stops.append(record['stop_name'])
        elif record['stop_type'] == 'F' and not record['stop_name'] in finish_stops:
            finish_stops.append(record['stop_name'])

        if record['bus_id'] not in stops.keys():
            stops[record['bus_id']] = [record['stop_name']]
        else:
            stops[record['bus_id']].append(record['stop_name'])

    for res in result:
        if not ('S' in result[res] and 'F' in result[res]):
            print('There is no start or end stop for the line:', res)
            return

    n_stops = {}
    for s in stops:
        for stop in stops[s]:
            if stop not in n_stops.keys():
                n_stops[stop] = 1
            else:
                n_stops[stop] += 1

    transfer_stops = []
    for stop in n_stops:
        if n_stops[stop] > 1:
            transfer_stops.append(stop)

    start_stops.sort()
    transfer_stops.sort()
    finish_stops.sort()

    print('Start stops:', len(start_stops), start_stops)
    print('Transfer stops:', len(transfer_stops), transfer_stops)
    print('Finish stops:', len(finish_stops), finish_stops)


def check_time(file):
    result = []
    bus2 = file[0]['bus_id']
    time2 = file[0]['a_time']
    station_error = False
    for record in file[1:]:
        bus1 = bus2
        time1 = time2

        if record['bus_id'] != bus1:
            bus2 = record['bus_id']
            time2 = record['a_time']
            station_error = False
            continue

        if station_error:
            continue

        bus2 = record['bus_id']
        time2 = record['a_time']
        station2 = record['stop_name']

        if not int(''.join(time2.split(':'))) % 2400 > int(''.join(time1.split(':'))) % 2400:
            station_error = True
            result.append(f'bus_id line {bus2}: wrong time on station {station2}')
            continue

    print('Arrival time test:')
    if not result:
        print('OK')
    else:
        for r in result:
            print(r)


def check_demand(file):
    stops = {}
    demand_stops = []
    for record in file:
        if record['stop_type'] == 'O' and record['stop_name'] not in demand_stops:
            demand_stops.append(record['stop_name'])

        if record['bus_id'] not in stops.keys():
            stops[record['bus_id']] = [record['stop_name']]
        else:
            stops[record['bus_id']].append(record['stop_name'])

    n_stops = {}
    for s in stops:
        for stop in stops[s]:
            if stop not in n_stops.keys():
                n_stops[stop] = 1
            else:
                n_stops[stop] += 1

    transfer_stops = []
    for stop in n_stops:
        if n_stops[stop] > 1:
            transfer_stops.append(stop)

    transfer_stops.sort()
    demand_stops.sort()

    wrongs = []
    for stop in demand_stops:
        if stop in transfer_stops:
            wrongs.append(stop)

    if wrongs:
        print('Wrong stop type:', wrongs)
    else:
        print('OK')


def main():
    file = json.loads(input())
    check_data(file)
    check_syntax(file)
    check_line(file)
    check_special(file)
    check_time(file)
    check_demand(file)


if __name__ == '__main__':
    main()
