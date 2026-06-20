from netmiko import ConnectHandler
from datetime import datetime
import os

os.makedirs("../reports", exist_ok=True)

devices = [
    {"device_type": "cisco_ios_telnet", "host": "192.168.20.128", "port": 5002},
    {"device_type": "cisco_ios_telnet", "host": "192.168.20.128", "port": 5004},
    {"device_type": "cisco_ios_telnet", "host": "192.168.20.128", "port": 5008},
]

dashboard = []

dashboard.append("=" * 60)
dashboard.append("NETWORK HEALTH DASHBOARD")
dashboard.append("=" * 60)
dashboard.append("")

for device in devices:

    try:
        conn = ConnectHandler(**device)
        conn.enable()

        hostname = conn.find_prompt().rstrip("#>").strip()

        # OSPF Check
        ospf_output = conn.send_command("show ip ospf neighbor")

        neighbors = 0
        for line in ospf_output.splitlines():
            if "FULL" in line:
                neighbors += 1

        ospf_status = "PASS" if neighbors > 0 else "FAIL"

        # Compliance Check
        run_config = conn.send_command("show running-config")
        ssh_output = conn.send_command("show ip ssh")

        compliance = "PASS"

        if "username admin" not in run_config:
            compliance = "FAIL"

        if "router ospf" not in run_config:
            compliance = "FAIL"

        if "version 2.0" not in ssh_output:
            compliance = "FAIL"

        # Interface Check
        int_output = conn.send_command("show ip interface brief")

        up_count = 0
        down_count = 0

        for line in int_output.splitlines()[1:]:

            if "up" in line.lower():
                up_count += 1

            elif "down" in line.lower():
                down_count += 1

        dashboard.append(f"Device      : {hostname}")
        dashboard.append(f"Status      : ONLINE")
        dashboard.append(f"OSPF        : {ospf_status}")
        dashboard.append(f"Compliance  : {compliance}")
        dashboard.append(f"Interfaces  : {up_count} UP / {down_count} DOWN")
        dashboard.append("-" * 60)

        conn.disconnect()

    except Exception as e:

        dashboard.append(f"Device      : PORT-{device['port']}")
        dashboard.append("Status      : OFFLINE")
        dashboard.append(f"Error       : {e}")
        dashboard.append("-" * 60)

dashboard.append("")
dashboard.append(f"Generated: {datetime.now()}")

with open(
    "../reports/network_health_dashboard.txt",
    "w",
    encoding="utf-8"
) as f:
    f.write("\n".join(dashboard))

print("\nDashboard generated successfully.")