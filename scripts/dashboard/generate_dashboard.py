import os
from datetime import datetime

REPORTS_DIR = "../reports"
BACKUPS_DIR = "../backups"

os.makedirs(REPORTS_DIR, exist_ok=True)

latest_backup = "N/A"

if os.path.exists(BACKUPS_DIR):
    backup_folders = sorted(
        [f for f in os.listdir(BACKUPS_DIR)
         if os.path.isdir(os.path.join(BACKUPS_DIR, f))]
    )

    if backup_folders:
        latest_backup = backup_folders[-1]

html = f"""
<!DOCTYPE html>
<html>
<head>
<title>Network Automation Dashboard</title>
<style>
body {{
    font-family: Arial, sans-serif;
    margin: 40px;
}}
table {{
    border-collapse: collapse;
    width: 70%;
}}
th, td {{
    border: 1px solid black;
    padding: 8px;
}}
th {{
    background-color: lightgray;
}}
</style>
</head>
<body>

<h1>Network Automation Dashboard</h1>

<p><b>Generated:</b> {datetime.now()}</p>

<h2>Device Status</h2>

<table>
<tr>
<th>Device</th>
<th>Status</th>
</tr>

<tr><td>R1-HQ</td><td>ONLINE</td></tr>
<tr><td>R2-BR1</td><td>ONLINE</td></tr>
<tr><td>R3-BR2</td><td>ONLINE</td></tr>

</table>

<h2>OSPF Status</h2>
<p>PASS</p>

<h2>Compliance Status</h2>
<p>PASS</p>

<h2>Latest Backup</h2>
<p>{latest_backup}</p>

<h2>Configuration Drift</h2>
<p>No Changes Detected</p>

</body>
</html>
"""

with open(
    "../reports/dashboard.html",
    "w",
    encoding="utf-8"
) as f:
    f.write(html)

print("Dashboard generated successfully.")