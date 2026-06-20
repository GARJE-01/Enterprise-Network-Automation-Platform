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
report.append("NETWORK COMPLIANCE REPORT")
report.append(f"Generated: {datetime.now()}")
report.append("=" * 50)
report.append("")

for device in devices:

    try:
        conn = ConnectHandler(**device)
        conn.enable()

        hostname = conn.find_prompt().rstrip("#>").strip()

        run_config = conn.send_command("show running-config")
        ssh_output = conn.send_command("show ip ssh")

        checks = {
            "Hostname": "PASS" if hostname else "FAIL",
            "Username Admin": "PASS" if "username admin" in run_config else "FAIL",
            "SSH Version 2": "PASS" if "version 2.0" in ssh_output else "FAIL",
            "OSPF Configured": "PASS" if "router ospf" in run_config else "FAIL",
            "Password Encryption": "PASS" if "service password-encryption" in run_config else "FAIL"
        }

        print(f"\n{hostname}")
        print("-" * 40)

        report.append(hostname)
        report.append("-" * 40)

        for item, result in checks.items():

            line = f"{item:<25} {result}"

            print(line)

            report.append(line)

        report.append("")

        conn.disconnect()

    except Exception as e:

        error = f"ERROR: {e}"

        print(error)

        report.append(error)

with open("../reports/compliance_report.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(report))

print("\nCompliance report saved successfully.")