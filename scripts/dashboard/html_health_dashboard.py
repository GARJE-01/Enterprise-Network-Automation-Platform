from netmiko import ConnectHandler
from datetime import datetime
import os

os.makedirs("../reports", exist_ok=True)

devices = [
    {"device_type": "cisco_ios_telnet", "host": "192.168.20.128", "port": 5002},
    {"device_type": "cisco_ios_telnet", "host": "192.168.20.128", "port": 5004},
    {"device_type": "cisco_ios_telnet", "host": "192.168.20.128", "port": 5008},
]

device_rows = ""

for device in devices:

    try:
        conn = ConnectHandler(**device)
        conn.enable()

        hostname = conn.find_prompt().rstrip("#>").strip()

        # OSPF Status
        ospf_output = conn.send_command("show ip ospf neighbor")
        neighbor_count = sum(
            1 for line in ospf_output.splitlines()
            if "FULL" in line
        )

        ospf_status = "PASS" if neighbor_count > 0 else "FAIL"

        # Compliance
        run_config = conn.send_command("show running-config")
        ssh_output = conn.send_command("show ip ssh")

        compliance = "PASS"

        if "username admin" not in run_config:
            compliance = "FAIL"

        if "router ospf" not in run_config:
            compliance = "FAIL"

        if "version 2.0" not in ssh_output:
            compliance = "FAIL"

        # Interface Summary
        int_output = conn.send_command("show ip interface brief")

        up_count = 0
        down_count = 0

        for line in int_output.splitlines()[1:]:

            line_lower = line.lower()

            if " up " in line_lower:
                up_count += 1

            elif "down" in line_lower:
                down_count += 1

        device_rows += f"""
        <tr>
            <td>{hostname}</td>
            <td>🟢 ONLINE</td>
            <td>{ospf_status}</td>
            <td>{compliance}</td>
            <td>{up_count} UP / {down_count} DOWN</td>
        </tr>
        """

        conn.disconnect()

    except Exception as e:

        device_rows += f"""
        <tr>
            <td>PORT-{device['port']}</td>
            <td>🔴 OFFLINE</td>
            <td>FAIL</td>
            <td>FAIL</td>
            <td>ERROR</td>
        </tr>
        """

html = f"""
<!DOCTYPE html>
<html>
<head>
<title>Network Automation Dashboard</title>

<style>

body {{
    font-family: Arial, sans-serif;
    margin: 30px;
    background-color: #f4f4f4;
}}

h1 {{
    text-align: center;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    background-color: white;
}}

th {{
    background-color: #333;
    color: white;
}}

th, td {{
    padding: 12px;
    border: 1px solid #ccc;
    text-align: center;
}}

.footer {{
    margin-top: 20px;
}}

</style>

</head>

<body>

<h1>Network Automation Dashboard</h1>

<p><strong>Generated:</strong> {datetime.now()}</p>

<table>

<tr>
    <th>Device</th>
    <th>Status</th>
    <th>OSPF</th>
    <th>Compliance</th>
    <th>Interfaces</th>
</tr>

{device_rows}

</table>

<div class="footer">
    <p><strong>Project:</strong> Enterprise Network Automation & Monitoring Platform</p>
</div>

</body>
</html>
"""

with open(
    "../reports/network_dashboard.html",
    "w",
    encoding="utf-8"
) as f:
    f.write(html)

print("HTML Dashboard generated successfully.")