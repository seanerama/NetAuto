# Network Latency Testing Script

This Python script is designed to test network latency between various network devices and multiple destinations. It dynamically identifies the primary and secondary data centers (DCs) for each device and pings them, along with other specified destinations, to gather and aggregate network performance data.

## Features

- **Dynamic Data Center Detection**: Automatically identifies the primary and secondary DC IP addresses for each device based on routing information.
- **Concurrent Ping Tests**: Uses multi-threading to efficiently ping multiple destinations from each device in parallel.
- **Aggregated Results**: Collects and aggregates ping results over time, with the ability to generate a daily summary CSV report.

## Prerequisites

- **Python 3.6+**
- **Netmiko**: For SSH connections to network devices.
- **PyYAML**: For loading configuration files.

You can install the necessary Python packages using:

```bash
pip install netmiko pyyaml
```
Configuration
The script relies on a config.yaml file for sensitive information, such as device credentials and email settings. Here is an example configuration:

```yaml

network_devices:
  cli_username: "your_username"
  cli_password: "your_password"

email:
  from_email: "your_email@example.com"
  send_server: "smtp.example.com"
```
Setup
test_destinations.txt
This file should contain a list of IP addresses or hostnames that the script will ping from each network device. Each line should contain one IP address or hostname.

Example:

```bash
8.8.8.8
1.1.1.1
10.0.0.1
google.com
domain.sharepoint.com
```
office_wan_devices.txt
This file should list the devices to be tested, with each line containing the device name and its management IP address, separated by a space.

Example:

```bash
HQ-Router-1 192.168.1.1
Branch-Router-2 192.168.2.1
```

Note: These files are included in .gitignore to prevent sensitive information from being accidentally committed to version control. Users will need to create their own versions of these files.

How the Script Works
Dynamic Data Center Detection
In the environment this script is designed for, each network device is connected to two data centers. The script identifies the primary and secondary DCs for each device by parsing the routing table and BGP information:

Primary DC: The script runs the command show ip route 0.0.0.0 | i , from on the device to determine the IP address of the primary DC.
Secondary DC: It then runs show ip bgp 0.0.0.0 | i from 1 to find the secondary DC IP, which is different from the primary DC IP.
Ping Testing
For each source device, the script pings the primary DC, secondary DC, and each destination listed in test_destinations.txt. It captures the minimum, average, and maximum round-trip times for each destination.

Aggregation
The script generates a CSV file every time it runs, storing the results for that run. At the end of the day, you can aggregate all the CSVs generated throughout the day into a single daily report. The aggregation takes the overall minimum, maximum, and average (computed across all averages) for each destination.

Running the Script
You can run the script manually by executing:

```bash

python net_test.py
```
To schedule the script to run every 15 minutes, you can use a cron job (on Linux):

```bash

*/15 * * * * /usr/bin/python3 /path/to/net_test.py
```
Aggregating Daily Results
To aggregate all the CSV files generated during the day into a single report, you can call the aggregate_test_daily() function:

```python
from net_test import aggregate_test_daily
aggregate_test_daily()
```
This will create a daily_aggregate_YYYYMMDD.csv file in the net_tests directory, summarizing the network performance data for the entire day.

Logging
The script logs its operations to net-test.log. This log file will contain information about the script's execution, including any errors encountered during SSH connections or command executions.

Contributions
Contributions are welcome! Please submit a pull request or open an issue to discuss changes.

License
This project is licensed under the MIT License. See the LICENSE file for details.



This `README.md` provides a comprehensive overview of how to set up, run, and understand the script, including how users should create their own `test_destinations.txt` and `office_wan_devices.txt` files. It also explains the script's dynamic behavior in detecting data centers and aggregating results.






