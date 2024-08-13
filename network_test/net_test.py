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
logging.basicConfig(filename='dnac_apis.log', level=logging.INFO, 
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
            ssh.send_command(f'ping {dest_ip} repeat 5', delay_factor=5, max_loops=1500, read_timeout=30)
            output = ssh.send_command(f'ping {dest_ip} repeat 5', delay_factor=5, max_loops=1500, read_timeout=30)

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
        print(results)
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
        headers = ['Primary-DC-min', 'Primary-DC-max', 'Primary-DC-avg', 'Secondary-DC-min', 'Secondary-DC-max', 'Secondary-DC-avg']
        for dest in destinations:
            headers.append(dest + '-min')
            headers.append(dest + '-avg')
            headers.append(dest + '-max')
        writer.writerow(headers)

        with ThreadPoolExecutor(max_workers=16) as executor:
            futures = [executor.submit(send_pings, source, destinations) for source in sources]
            for future in futures:
                source_name, source_ip, results = future.result()
                row = [source_name, source_ip]
                print(results)
                row.extend(results.get('Primary-DC', (None, None, None)))
                row.extend(results.get('Secondary-DC', (None, None, None)))
                for dest in destinations:
                    row.extend(results.get(dest, (None, None, None)))
                writer.writerow(row)

if __name__ == "__main__":
    main()

