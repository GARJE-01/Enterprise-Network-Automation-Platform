from netmiko import ConnectHandler
import os
from datetime import datetime

os.makedirs("../reports", exist_ok=True)

devices = [
    {"device_type": "cisco_ios_telnet", "host": "192.168.20.128", "port": 5002},
    {"device_type": "cisco_ios_telnet", "host": "192.168.20.128", "port": 5004},
    {"device_type": "cisco_ios_telnet", "host": "192.168.20.128", "port": 5008},
]

report = []

report.append("=" * 50)
report.append("INTERFACE STATUS REPORT")
report.append(f"Generated: {datetime.now()}")
report.append("=" * 50)
report.append("")

for device in devices:

    try:
        conn = ConnectHandler(**device)
        conn.enable()

        hostname = conn.find_prompt().rstrip("#>").strip()

        output = conn.send_command("show ip interface brief")

        print(f"\n{hostname}")
        print("-" * 50)

        report.append(hostname)
        report.append("-" * 50)

        lines = output.splitlines()

        for line in lines[1:]:

            if not line.strip():
                continue

            parts = line.split()

            if len(parts) >= 6:

                interface = parts[0]
                ip = parts[1]
                status = parts[-2]
                protocol = parts[-1]

                state = "PASS"

                if "down" in status.lower():
                    state = "FAIL"

                report_line = (
                    f"{interface:<20} "
                    f"{status:<15} "
                    f"{protocol:<10} "
                    f"{state}"
                )

                print(report_line)
                report.append(report_line)

        report.append("")

        conn.disconnect()

    except Exception as e:
        report.append(f"ERROR: {e}")

with open(
    "../reports/interface_status_report.txt",
    "w",
    encoding="utf-8"
) as f:
    f.write("\n".join(report))

print("\nInterface report generated successfully.")