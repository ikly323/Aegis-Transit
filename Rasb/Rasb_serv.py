import socket
import sys
import os
import time
import json
import re
from statistics import mean


def parse_stdin_config():
    stdin_data = sys.stdin.read()
    if not stdin_data:
        raise ValueError("Empty contract")
    try:
        config = json.loads(stdin_data)
        first_key = next(iter(config))
        sensors = config[first_key]
        sensor_ranges = {}
        for sensor in sensors:
            if sensor['key'] in ['temperature', 'light', 'press']:
                if '/' in sensor['value']:
                    min_val, max_val = map(float, sensor['value'].split('/'))
                    sensor_ranges[sensor['key']] = (min_val, max_val)
        return sensor_ranges
    except json.JSONDecodeError:
        return {}


def parse_sensor_data(data_string):
    pattern = r'\{(\w+):([\d.]+)\}'
    matches = re.findall(pattern, data_string)
    sensors = {}
    for sensor_name, value in matches:
        if sensor_name in ['temperature', 'light', 'press']:
            sensors[sensor_name] = float(value)
    return sensors


def check_ranges(sensor_values, sensor_ranges):
    results = {}
    for sensor_name in ['temperature', 'light', 'press']:
        values = sensor_values.get(sensor_name, [])
        if values and sensor_name in sensor_ranges:
            min_range, max_range = sensor_ranges[sensor_name]
            avg_value = mean(values)
            results[sensor_name] = {
                'avg': avg_value,
                'min_range': min_range,
                'max_range': max_range,
                'within': min_range <= avg_value <= max_range,
                'count': len(values)
            }
    return results


def print_results(results):
    print("\n" + "=" * 50)
    print("SENSOR VALIDATION RESULTS")
    print("=" * 50)
    for sensor_name, data in results.items():
        status = "OK" if data['within'] else "FAIL"
        color = 32 if data['within'] else 31
        print(f"\n{sensor_name.upper():<15} {status}")
        print(f"  Average:   {data['avg']:>10.2f}")
        print(f"  Required:  {data['min_range']:>5.0f} - {data['max_range']:>5.0f}")
        print(f"  Samples:   {data['count']:>10}")
        if not data['within']:
            if data['avg'] < data['min_range']:
                diff = data['min_range'] - data['avg']
                print(f"  Too low by: {diff:>10.2f}")
            else:
                diff = data['avg'] - data['max_range']
                print(f"  Too height by: {diff:>10.2f}")
    print("\n" + "=" * 50)
    all_ok = all(data['within'] for data in results.values())
    if all_ok:
        print("\033[32m ALL SENSORS WITHIN RANGE\033[0m")
    else:
        print("\033[31m SOME SENSORS OUT OF RANGE\033[0m")
    print("=" * 50)


def main():
    sensor_ranges = parse_stdin_config()
    if not sensor_ranges:
        print("No valid sensor ranges found in input")
        return
    print("Sensor ranges from config:")
    for sensor, (min_val, max_val) in sensor_ranges.items():
        print(f"  {sensor}: {min_val} - {max_val}")
    sensor_values = {
        'temperature': [],
        'light': [],
        'press': []
    }
    host = "0.0.0.0"
    port = 55555
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(5)
        server_socket.settimeout(0.1)
        print(f"\nServer listening on port {port}")
        print("Waiting for sensor data...")
        print("-" * 50)
        while True:
            try:
                client_socket, client_address = server_socket.accept()
                client_socket.sendall(b"READY")
                client_socket.settimeout(2.0)
                try:
                    raw_data = client_socket.recv(4096)
                    if raw_data:
                        data_string = raw_data.decode('utf-8', errors='ignore')
                        sensors = parse_sensor_data(data_string)
                        for sensor_name, value in sensors.items():
                            sensor_values[sensor_name].append(value)
                            print(f"Received {sensor_name}: {value}")
                except socket.timeout:
                    pass
                client_socket.close()
            except socket.timeout:
                pass
            except KeyboardInterrupt:
                break
            except Exception:
                continue
            if os.path.exists("FLAG_FILE.txt"):
                print("\n" + "!" * 50)
                print("!!! FLAG_FILE.txt DETECTED !!!")
                print("!" * 50)
                results = check_ranges(sensor_values, sensor_ranges)
                print_results(results)
                break
            time.sleep(0.5)


if __name__ == "__main__":
    main()
