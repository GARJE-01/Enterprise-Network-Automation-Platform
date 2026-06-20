from netmiko import ConnectHandler
from datetime import datetime
import os

os.makedirs("../reports", exist_ok=True)

routers = [
    {"device_type": "cisco_ios_telnet", "host": "192.168.20.128", "port": 5002},
    {"device_type": "cisco_ios_telnet", "host": "192.168.20.128", "port": 5004},
    {"device_type": "cisco_ios_telnet", "host": "192.168.20.128", "port": 5008},
]

switches = [
    {"device_type": "cisco_ios_telnet", "host": "192.168.20.128", "port": 5000},
    {"device_type": "cisco_ios_telnet", "host": "192.168.20.128", "port": 5006},
]

router_summary_rows = ""
switch_summary_rows = ""
device_details = ""

online_devices = 0

# =========================
# ROUTERS
# =========================

for device in routers:

    try:
        conn = ConnectHandler(**device)
        conn.enable()

        hostname = conn.find_prompt().rstrip("#>").strip()

        online_devices += 1

        interfaces = conn.send_command(
            "show ip interface brief",
            read_timeout=30
        )

        ospf = conn.send_command(
            "show ip ospf neighbor",
            read_timeout=30
        )

        running_config = conn.send_command(
            "show running-config",
            read_timeout=60
        )

        neighbor_count = sum(
            1 for line in ospf.splitlines()
            if "FULL" in line
        )

        ospf_status = "PASS" if neighbor_count > 0 else "FAIL"

        router_summary_rows += f"""
        <tr>
            <td>{hostname}</td>
            <td>ONLINE</td>
            <td>{ospf_status}</td>
            <td>{neighbor_count}</td>
        </tr>
        """

        device_details += f"""
        <details>
        <summary><b>{hostname}</b></summary>

        <h3>Interfaces</h3>
        <pre>{interfaces}</pre>

        <h3>OSPF Neighbors</h3>
        <pre>{ospf}</pre>

        <h3>Running Configuration</h3>
        <pre>{running_config}</pre>

        </details>
        <hr>
        """

        conn.disconnect()

    except Exception as e:

        router_summary_rows += f"""
        <tr>
            <td>PORT-{device['port']}</td>
            <td>OFFLINE</td>
            <td>FAIL</td>
            <td>0</td>
        </tr>
        """

# =========================
# SWITCHES
# =========================

for device in switches:

    try:
        conn = ConnectHandler(**device)
        conn.enable()

        hostname = conn.find_prompt().rstrip("#>").strip()

        online_devices += 1

        vlan_output = conn.send_command(
            "show vlan brief",
            read_timeout=30
        )

        interfaces = conn.send_command(
            "show ip interface brief",
            read_timeout=30
        )

        running_config = conn.send_command(
            "show running-config",
            read_timeout=60
        )

        vlan_count = vlan_output.count("active")

        switch_summary_rows += f"""
        <tr>
            <td>{hostname}</td>
            <td>ONLINE</td>
            <td>{vlan_count}</td>
        </tr>
        """

        device_details += f"""
        <details>
        <summary><b>{hostname}</b></summary>

        <h3>Interfaces</h3>
        <pre>{interfaces}</pre>

        <h3>VLAN Information</h3>
        <pre>{vlan_output}</pre>

        <h3>Running Configuration</h3>
        <pre>{running_config}</pre>

        </details>
        <hr>
        """

        conn.disconnect()

    except Exception as e:

        switch_summary_rows += f"""
        <tr>
            <td>PORT-{device['port']}</td>
            <td>OFFLINE</td>
            <td>0</td>
        </tr>
        """

# =========================
# HTML DASHBOARD
# =========================

html = f"""
<!DOCTYPE html>
<html>
<head>

<title>Network Operations Dashboard</title>

<style>

body {{
    font-family: Arial, sans-serif;
    margin: 25px;
    background-color: #f5f5f5;
}}

h1 {{
    text-align: center;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    background-color: white;
    margin-bottom: 25px;
}}

th {{
    background-color: #333;
    color: white;
}}

th, td {{
    border: 1px solid #ccc;
    padding: 10px;
    text-align: center;
}}

details {{
    background: white;
    padding: 10px;
    margin-bottom: 10px;
}}

pre {{
    background: #f0f0f0;
    padding: 10px;
    overflow-x: auto;
}}

</style>

</head>

<body>

<h1>Network Operations Dashboard</h1>

<p><b>Generated:</b> {datetime.now()}</p>

<h2>Network Overview</h2>

<ul>
<li>Total Devices: 5</li>
<li>Online Devices: {online_devices}</li>
<li>Routers: 3</li>
<li>Switches: 2</li>
</ul>

<h2>Router Summary</h2>

<table>

<tr>
<th>Router</th>
<th>Status</th>
<th>OSPF</th>
<th>Neighbors</th>
</tr>

{router_summary_rows}

</table>

<h2>Switch Summary</h2>

<table>

<tr>
<th>Switch</th>
<th>Status</th>
<th>VLAN Count</th>
</tr>

{switch_summary_rows}

</table>

<h2>Device Details</h2>

{device_details}

</body>
</html>
"""

with open(
    "../reports/network_operations_dashboard.html",
    "w",
    encoding="utf-8"
) as f:
    f.write(html)

print("\nDashboard generated successfully!")
print("\nOpen:")
print("../reports/network_operations_dashboard.html")