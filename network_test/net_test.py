from netmiko import ConnectHandler
import csv
import re
import datetime
import logging
import yaml
from concurrent.futures import ThreadPoolExecutor
import os

# Load the config file
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

def generate_test_id():
    # Current date and time
    now = datetime.datetime.now()
    # Format the ID as specified: 'NT' + MM + DD + YYYY + HHMM
    test_id = now.strftime("NT%m%d%Y%H%M")
    return test_id

# Configure logging
logging.basicConfig(filename='net-test.log', level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

user = config['network_devices']['cli_username']
pwd = config['network_devices']['cli_password']

def get_destinations(filename='test_destinations.txt'):
    """Read a list of IPs from a text file."""
    with open(filename, 'r', encoding='utf-8-sig') as dest_file:
        dests = [line.strip() for line in dest_file]
    return dests

def get_sources(filename='office_wan_devices.txt'):
    """Read a list of IPs from a text file."""
    with open(filename, 'r', encoding='utf-8-sig') as source_file:
        sources = [line.strip() for line in source_file]
    return sources

destinations = get_destinations()
sources = get_sources()

def send_pings(source, destinations):
    destination_names = ['Primary-DC', 'Secondary-DC']
    source_name, source_ip = source.split(' ')
    cisco_router = {
        'device_type': 'cisco_ios', 'host': source_ip, 'username': user,
        'password': pwd, 'secret': pwd, 'port': 22, 'timeout': 100, 'conn_timeout': 60
    }
    dests_ips = []
    results = {}
    try:
        ssh = ConnectHandler(**cisco_router)
        #get primary and secondary dcs
        def_route = ssh.send_command('show ip route 0.0.0.0 | i , from')
        primary_dc = re.findall(r'\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}', def_route)
        primary_dc_ip = primary_dc[0]
        sec_route = ssh.send_command('show ip bgp 0.0.0.0 | i from 1')
        ips = re.findall(r' \d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}', sec_route)
        secondary_dc_ip = [ip for ip in ips if ip != primary_dc_ip][0]
        dests_ips.append(primary_dc_ip)
        dests_ips.append(secondary_dc_ip)
        for dest in destinations:
            dests_ips.append(dest)
            destination_names.append(dest)
        x = 0
        for dest_ip in dests_ips:       
            #pinging once 
            print(ssh.send_command(f'ping {dest_ip} source lo0', delay_factor=5, max_loops=1500, read_timeout=30))
            output = ssh.send_command(f'ping {dest_ip} source lo0', delay_factor=5, max_loops=1500, read_timeout=30)
            success_rate = re.search(r'Success rate is (\d+) percent', output)
            response = re.findall(r'round-trip min/avg/max = \d+/\d+/\d+ ms', output)

            if success_rate and int(success_rate.group(1)) > 0 and response[0]:
                times = re.findall(r'\d+',response[0])
                min_time = times[0]
                avg_time = times[1]
                max_time = times[2]
                results[destination_names[x]]= min_time, avg_time, max_time
            else:
                results[destination_names[x]] = (None, None, None)
            x = x + 1
        ssh.disconnect()
    except Exception as e:
        print(f"Failed to connect or send command to {source_ip}: {e}")
        results = {destination_names[x]: ('ERROR', 'ERROR', 'ERROR') for dest_ip in dests_ips}

    return source_ip, source_name, results

def main():
    # Ensure the 'net_tests' directory exists
    os.makedirs('net_tests', exist_ok=True)
    # Generate the filename with the directory prepended
    filename = 'net_tests/' + generate_test_id() + '.csv'
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        # Adjust the header to include SourceName,SourceIP,'Primary-DC-min', 'Primary-DC-max', 'Primary-DC-avg', 'Secondary-DC-min', 'Secondary-DC-max', 'Secondary-DC-avg' then for each destination in destinations add min max and avg
        headers = ['Source-IP', 'Name', 'Primary-DC-min', 'Primary-DC-max', 'Primary-DC-avg', 'Secondary-DC-min', 'Secondary-DC-max', 'Secondary-DC-avg']
        for dest in destinations:
            headers.append(dest + '-min')
            headers.append(dest + '-avg')
            headers.append(dest + '-max')
        writer.writerow(headers)

        with ThreadPoolExecutor(max_workers=40) as executor:
            futures = [executor.submit(send_pings, source, destinations) for source in sources]
            for future in futures:
                source_name, source_ip, results = future.result()
                row = [source_name, source_ip]
                row.extend(results.get('Primary-DC', (None, None, None)))
                row.extend(results.get('Secondary-DC', (None, None, None)))
                for dest in destinations:
                    row.extend(results.get(dest, (None, None, None)))
                writer.writerow(row)

def aggregate_test_daily():
    # Directory where individual test CSVs are stored
    directory = 'net_tests'
    
    # Initialize dictionaries to store the aggregate values
    aggregate_data = {}
    file_count = 0

    # Iterate over all CSV files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            file_count += 1
            filepath = os.path.join(directory, filename)
            
            with open(filepath, 'r') as file:
                reader = csv.reader(file)
                headers = next(reader)  # Skip the header row
                
                for row in reader:
                    source_name = row[0]
                    source_ip = row[1]
                    
                    # Aggregate data for each destination
                    for i in range(2, len(row), 3):  # Skip source_name and source_ip
                        dest_name = headers[i].replace('-min', '')
                        min_time = int(row[i]) if row[i] and row[i] != 'None' else None
                        avg_time = int(row[i+1]) if row[i+1] and row[i+1] != 'None' else None
                        max_time = int(row[i+2]) if row[i+2] and row[i+2] != 'None' else None

                        if dest_name not in aggregate_data:
                            aggregate_data[dest_name] = {'min': min_time, 'max': max_time, 'avg': avg_time, 'avg_count': 1}
                        else:
                            if min_time is not None and (aggregate_data[dest_name]['min'] is None or min_time < aggregate_data[dest_name]['min']):
                                aggregate_data[dest_name]['min'] = min_time
                            if max_time is not None and (aggregate_data[dest_name]['max'] is None or max_time > aggregate_data[dest_name]['max']):
                                aggregate_data[dest_name]['max'] = max_time
                            if avg_time is not None:
                                if aggregate_data[dest_name]['avg'] is None:
                                    aggregate_data[dest_name]['avg'] = avg_time
                                else:
                                    aggregate_data[dest_name]['avg'] += avg_time
                                aggregate_data[dest_name]['avg_count'] += 1
    
    # Calculate the final average for each destination
    for dest_name, data in aggregate_data.items():
        if data['avg'] is not None:
            data['avg'] = data['avg'] / data['avg_count']

    # Write the aggregated data to a new CSV file
    aggregated_filename = os.path.join(directory, 'daily_aggregate_' + datetime.datetime.now().strftime('%Y%m%d') + '.csv')
    
    with open(aggregated_filename, 'w', newline='') as file:
        writer = csv.writer(file)
        headers = ['Destination', 'Min Time', 'Avg Time', 'Max Time']
        writer.writerow(headers)
        
        for dest_name, data in aggregate_data.items():
            row = [dest_name, data['min'], data['avg'], data['max']]
            writer.writerow(row)
    
    print(f"Aggregated data from {file_count} files into {aggregated_filename}")
    return(f"Aggregated data from {file_count} files into {aggregated_filename}")

if __name__ == "__main__":
    main()

