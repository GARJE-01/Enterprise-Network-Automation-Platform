from netmiko import ConnectHandler
from datetime import datetime
import os

os.makedirs("../reports", exist_ok=True)

BACKUP_DIR = "../backups"
DRIFT_DIR = "../drift_reports"

routers = [
    {"device_type":"cisco_ios_telnet","host":"192.168.20.128","port":5002},
    {"device_type":"cisco_ios_telnet","host":"192.168.20.128","port":5004},
    {"device_type":"cisco_ios_telnet","host":"192.168.20.128","port":5008},
]

switches = [
    {"device_type":"cisco_ios_telnet","host":"192.168.20.128","port":5000},
    {"device_type":"cisco_ios_telnet","host":"192.168.20.128","port":5006},
]

devices_data = []

online_devices = 0
online_routers = 0
online_switches = 0

ospf_healthy = 0
compliance_pass = 0

total_health_score = 0
total_devices_scored = 0

print("\nCollecting Network Data...\n")


# ==========================================
# ROUTERS
# ==========================================

for device in routers:

    try:

        conn = ConnectHandler(**device)
        conn.enable()

        hostname = conn.find_prompt().rstrip("#>").strip()

        print(f"Connected -> {hostname}")

        online_devices += 1
        online_routers += 1

        int_brief = conn.send_command(
            "show ip interface brief",
            read_timeout=30
        )

        run_cfg = conn.send_command(
            "show running-config",
            read_timeout=90
        )

        ospf_out = conn.send_command(
            "show ip ospf neighbor",
            read_timeout=30
        )

        ssh_out = conn.send_command(
            "show ip ssh",
            read_timeout=30
        )

        neighbors = sum(
            1
            for line in ospf_out.splitlines()
            if "FULL" in line
        )

        ospf_ok = neighbors > 0

        if ospf_ok:
            ospf_healthy += 1

        compliance_ok = (
            "username admin" in run_cfg and
            "router ospf" in run_cfg and
            "version 2.0" in ssh_out
        )

        if compliance_ok:
            compliance_pass += 1

        score = 25

        if ospf_ok:
            score += 25

        if compliance_ok:
            score += 25

        score += 25

        total_health_score += score
        total_devices_scored += 1

        devices_data.append({

            "type": "router",

            "hostname": hostname,

            "interfaces": int_brief,

            "ospf": ospf_out,

            "config": run_cfg,

            "neighbors": neighbors,

            "ospf_ok": ospf_ok,

            "compliance_ok": compliance_ok,

            "health": score

        })

        conn.disconnect()

    except Exception as e:

        print(f"Router Error: {e}")



# ==========================================
# SWITCHES
# ==========================================

for device in switches:

    try:

        conn = ConnectHandler(**device)
        conn.enable()

        hostname = conn.find_prompt().rstrip("#>").strip()

        print(f"Connected -> {hostname}")

        online_devices += 1
        online_switches += 1

        vlan_output = conn.send_command(
            "show vlan brief",
            read_timeout=30
        )

        run_cfg = conn.send_command(
            "show running-config",
            read_timeout=90
        )

        score = 100

        total_health_score += score
        total_devices_scored += 1

        devices_data.append({

            "type": "switch",

            "hostname": hostname,

            "vlan": vlan_output,

            "config": run_cfg,

            "health": score

        })

        conn.disconnect()

    except Exception as e:

        print(f"Switch Error: {e}")# ==========================================
# HEALTH SUMMARY
# ==========================================

avg_health = 0

if total_devices_scored:
    avg_health = round(
        total_health_score / total_devices_scored,
        1
    )

router_summary_rows = ""
switch_summary_rows = ""

compliance_rows = ""
ospf_rows = ""
vlan_rows = ""

device_sections = ""


# ==========================================
# BUILD DEVICE TABLES
# ==========================================

for device in devices_data:

    # ==========================
    # ROUTERS
    # ==========================

    if device["type"] == "router":

        router_summary_rows += f"""
        <tr>
        <td>{device['hostname']}</td>
        <td>ONLINE</td>
        <td>{device['health']}/100</td>
        <td>{"PASS" if device['ospf_ok'] else "FAIL"}</td>
        </tr>
        """

        compliance_rows += f"""
        <tr>
        <td>{device['hostname']}</td>
        <td>{"PASS" if device['compliance_ok'] else "FAIL"}</td>
        </tr>
        """

        ospf_rows += f"""
        <tr>
        <td>{device['hostname']}</td>
        <td>{device['neighbors']}</td>
        <td>{"HEALTHY" if device['ospf_ok'] else "DOWN"}</td>
        </tr>
        """

        device_sections += f"""
        <details class="device">

        <summary>
        🛣️ ROUTER - {device['hostname']}
        </summary>

        <h3>Interfaces</h3>
        <pre>
{device['interfaces']}
        </pre>

        <h3>OSPF Neighbors</h3>
        <pre>
{device['ospf']}
        </pre>

        <h3>Running Configuration</h3>
        <pre>
{device['config']}
        </pre>

        </details>
        """

    # ==========================
    # SWITCHES
    # ==========================

    else:

        vlan10 = "10   USERS" in device["vlan"]
        vlan20 = "20   SERVERS" in device["vlan"]
        vlan99 = "99   MGMT" in device["vlan"]

        switch_summary_rows += f"""
        <tr>
        <td>{device['hostname']}</td>
        <td>ONLINE</td>
        <td>{device['health']}/100</td>
        </tr>
        """

        vlan_rows += f"""
        <tr>
        <td>{device['hostname']}</td>
        <td>{"YES" if vlan10 else "NO"}</td>
        <td>{"YES" if vlan20 else "NO"}</td>
        <td>{"YES" if vlan99 else "NO"}</td>
        </tr>
        """

        device_sections += f"""
        <details class="device">

        <summary>
        🔀 SWITCH - {device['hostname']}
        </summary>

        <h3>VLAN Information</h3>

        <pre>
{device['vlan']}
        </pre>

        <h3>Running Configuration</h3>

        <pre>
{device['config']}
        </pre>

        </details>
        """


# ==========================================
# BACKUP DASHBOARD
# ==========================================

backup_count = 0
latest_backup = "N/A"

backup_rows = ""

if os.path.exists(BACKUP_DIR):

    backup_folders = sorted(
        [
            f for f in os.listdir(BACKUP_DIR)
            if os.path.isdir(
                os.path.join(BACKUP_DIR, f)
            )
        ]
    )

    backup_count = len(backup_folders)

    if backup_folders:
        latest_backup = backup_folders[-1]

    for folder in reversed(backup_folders):

        files = os.listdir(
            os.path.join(
                BACKUP_DIR,
                folder
            )
        )

        backup_rows += f"""
        <tr>
        <td>{folder}</td>
        <td>{len(files)}</td>
        </tr>
        """


# ==========================================
# DRIFT DASHBOARD
# ==========================================

drift_rows = ""

if os.path.exists(DRIFT_DIR):

    drift_files = sorted(
        [
            f
            for f in os.listdir(DRIFT_DIR)
            if f.endswith(".txt")
        ]
    )

    for file in reversed(drift_files):

        try:

            path = os.path.join(
                DRIFT_DIR,
                file
            )

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:

                content = f.read()

            preview = content[:1200]

            drift_rows += f"""
            <details>

            <summary>
            {file}
            </summary>

            <pre>
{preview}
            </pre>

            </details>
            """

        except Exception as e:

            drift_rows += f"""
            <p>
            Error Reading:
            {file}
            </p>
            """# ==========================================
# HTML DASHBOARD
# ==========================================

html = f"""
<!DOCTYPE html>

<html>

<head>

<title>
Unified Network Operations Dashboard V2
</title>

<style>

body {{
    background:#111;
    color:white;
    font-family:Arial;
    margin:20px;
}}

h1 {{
    text-align:center;
}}

.card {{
    display:inline-block;
    background:#222;
    padding:20px;
    margin:10px;
    border-radius:10px;
    min-width:180px;
    text-align:center;
}}

.card h2 {{
    margin:0;
}}

table {{
    width:100%;
    border-collapse:collapse;
    margin-bottom:30px;
}}

th {{
    background:#333;
}}

td,th {{
    border:1px solid #555;
    padding:10px;
    text-align:center;
}}

details {{
    background:#222;
    margin-bottom:10px;
    padding:10px;
    border-radius:8px;
}}

summary {{
    cursor:pointer;
    font-size:17px;
}}

pre {{
    background:black;
    color:#00ff00;
    padding:10px;
    overflow:auto;
}}

input {{
    width:100%;
    padding:12px;
    margin-bottom:15px;
    font-size:16px;
}}

button {{
    padding:10px;
    margin-right:10px;
    margin-bottom:20px;
}}

.section {{
    margin-top:40px;
}}

</style>

<script>

function searchDevices() {{

    let input =
        document.getElementById("search")
        .value
        .toLowerCase();

    let devices =
        document.getElementsByClassName("device");

    for(let i=0;i<devices.length;i++) {{

        let text =
            devices[i].innerText.toLowerCase();

        if(text.includes(input))
            devices[i].style.display="block";

        else
            devices[i].style.display="none";
    }}
}}

function expandAll() {{

    document
    .querySelectorAll("details")
    .forEach(
        d => d.open = true
    );
}}

function collapseAll() {{

    document
    .querySelectorAll("details")
    .forEach(
        d => d.open = false
    );
}}

</script>

</head>

<body>

<h1>
🚀 Unified Network Operations Dashboard V2
</h1>

<p>
Generated:
{datetime.now()}
</p>

<!-- =================================== -->
<!-- STATUS CARDS -->
<!-- =================================== -->

<div class="section">

<div class="card">
<h3>Devices Online</h3>
<h2>{online_devices}/5</h2>
</div>

<div class="card">
<h3>Routers</h3>
<h2>{online_routers}/3</h2>
</div>

<div class="card">
<h3>Switches</h3>
<h2>{online_switches}/2</h2>
</div>

<div class="card">
<h3>OSPF Healthy</h3>
<h2>{ospf_healthy}/3</h2>
</div>

<div class="card">
<h3>Compliance</h3>
<h2>{compliance_pass}/3</h2>
</div>

<div class="card">
<h3>Avg Health</h3>
<h2>{avg_health}%</h2>
</div>

</div>

<!-- =================================== -->
<!-- ROUTER SUMMARY -->
<!-- =================================== -->

<div class="section">

<h2>Router Summary</h2>

<table>

<tr>
<th>Router</th>
<th>Status</th>
<th>Health</th>
<th>OSPF</th>
</tr>

{router_summary_rows}

</table>

</div>

<!-- =================================== -->
<!-- SWITCH SUMMARY -->
<!-- =================================== -->

<div class="section">

<h2>Switch Summary</h2>

<table>

<tr>
<th>Switch</th>
<th>Status</th>
<th>Health</th>
</tr>

{switch_summary_rows}

</table>

</div>

<!-- =================================== -->
<!-- COMPLIANCE -->
<!-- =================================== -->

<div class="section">

<h2>Compliance Dashboard</h2>

<table>

<tr>
<th>Router</th>
<th>Status</th>
</tr>

{compliance_rows}

</table>

</div>

<!-- =================================== -->
<!-- OSPF -->
<!-- =================================== -->

<div class="section">

<h2>OSPF Dashboard</h2>

<table>

<tr>
<th>Router</th>
<th>Neighbors</th>
<th>Status</th>
</tr>

{ospf_rows}

</table>

</div>

<!-- =================================== -->
<!-- VLAN -->
<!-- =================================== -->

<div class="section">

<h2>VLAN Dashboard</h2>

<table>

<tr>
<th>Switch</th>
<th>VLAN10</th>
<th>VLAN20</th>
<th>VLAN99</th>
</tr>

{vlan_rows}

</table>

</div>

<!-- =================================== -->
<!-- BACKUPS -->
<!-- =================================== -->

<div class="section">

<h2>Backup Dashboard</h2>

<div class="card">
<h3>Total Backup Sets</h3>
<h2>{backup_count}</h2>
</div>

<div class="card">
<h3>Latest Backup</h3>
<h2>{latest_backup}</h2>
</div>

<table>

<tr>
<th>Backup Folder</th>
<th>Files</th>
</tr>

{backup_rows}

</table>

</div>

<!-- =================================== -->
<!-- DRIFT -->
<!-- =================================== -->

<div class="section">

<h2>Drift Detection Dashboard</h2>

{drift_rows}

</div>

<!-- =================================== -->
<!-- SEARCH -->
<!-- =================================== -->

<div class="section">

<h2>Search Network</h2>

<input
type="text"
id="search"
placeholder="Search hostname, interface, vlan, ospf, config..."
onkeyup="searchDevices()"
>

<button onclick="expandAll()">
Expand All
</button>

<button onclick="collapseAll()">
Collapse All
</button>

</div>

<!-- =================================== -->
<!-- DEVICE EXPLORER -->
<!-- =================================== -->

<div class="section">

<h2>Device Explorer</h2>

{device_sections}

</div>

</body>

</html>
"""

# ==========================================
# SAVE DASHBOARD
# ==========================================

output_file = (
    "../reports/network_operations_dashboard_v2.html"
)

with open(
    output_file,
    "w",
    encoding="utf-8"
) as f:

    f.write(html)

print("\n====================================")
print("Dashboard Generated Successfully")
print("====================================")
print(f"\nFile: {output_file}")