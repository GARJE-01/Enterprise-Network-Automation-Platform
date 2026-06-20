from netmiko import ConnectHandler
import os
from datetime import datetime

# Create reports folder if it doesn't exist
os.makedirs("../reports", exist_ok=True)

devices = [
    {"device_type": "cisco_ios_telnet", "host": "192.168.20.128", "port": 5002},
    {"device_type": "cisco_ios_telnet", "host": "192.168.20.128", "port": 5004},
    {"device_type": "cisco_ios_telnet", "host": "192.168.20.128", "port": 5008},
]

report_lines = []

report_lines.append("=" * 40)
report_lines.append("OSPF HEALTH REPORT")
report_lines.append(f"Generated: {datetime.now()}")
report_lines.append("=" * 40)
report_lines.append("")

print("\n" + "=" * 40)
print("OSPF HEALTH REPORT")
print("=" * 40 + "\n")

for device in devices:
    try:
        conn = ConnectHandler(**device)
        conn.enable()

        hostname = conn.find_prompt().rstrip("#>").strip()

        output = conn.send_command("show ip ospf neighbor")

        neighbor_count = 0

        for line in output.splitlines():
            if "FULL" in line:
                neighbor_count += 1

        status = "PASS" if neighbor_count > 0 else "FAIL"

        print(f"{hostname}")
        print(f"Neighbors : {neighbor_count}")
        print(f"Status    : {status}")
        print("-" * 30)

        report_lines.append(f"Device    : {hostname}")
        report_lines.append(f"Neighbors : {neighbor_count}")
        report_lines.append(f"Status    : {status}")
        report_lines.append("-" * 30)

        conn.disconnect()

    except Exception as e:
        print(f"ERROR: {e}")

        report_lines.append(f"ERROR on device port {device['port']}")
        report_lines.append(str(e))
        report_lines.append("-" * 30)

# Save report
report_file = "../reports/ospf_health_report.txt"

with open(report_file, "w", encoding="utf-8") as file:
    file.write("\n".join(report_lines))

print(f"\nReport saved to: {report_file}")