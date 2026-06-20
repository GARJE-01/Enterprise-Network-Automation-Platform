from netmiko import ConnectHandler
import csv
import os

os.makedirs("../reports", exist_ok=True)

devices = [
    {"device_type": "cisco_ios_telnet", "host": "192.168.20.128", "port": 5002},
    {"device_type": "cisco_ios_telnet", "host": "192.168.20.128", "port": 5004},
    {"device_type": "cisco_ios_telnet", "host": "192.168.20.128", "port": 5008},
]

rows = []

for device in devices:

    try:
        conn = ConnectHandler(**device)
        conn.enable()

        hostname = conn.find_prompt().rstrip("#>").strip()

        rows.append([
            hostname,
            device["port"],
            "ONLINE"
        ])

        conn.disconnect()

    except:
        rows.append([
            f"PORT-{device['port']}",
            device["port"],
            "OFFLINE"
        ])

with open(
    "../reports/network_inventory.csv",
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "Hostname",
        "Port",
        "Status"
    ])

    writer.writerows(rows)

print("CSV inventory exported successfully.")