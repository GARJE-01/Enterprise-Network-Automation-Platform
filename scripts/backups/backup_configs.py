from netmiko import ConnectHandler
from datetime import datetime
import os

devices = [
    {"device_type": "cisco_ios_telnet", "host": "192.168.20.128", "port": 5002},
    {"device_type": "cisco_ios_telnet", "host": "192.168.20.128", "port": 5004},
    {"device_type": "cisco_ios_telnet", "host": "192.168.20.128", "port": 5008},
]

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

backup_folder = f"../backups/{timestamp}"

os.makedirs(backup_folder, exist_ok=True)

for device in devices:

    try:
        conn = ConnectHandler(**device)
        conn.enable()

        hostname = conn.find_prompt().rstrip("#>").strip()

        print(f"Backing up {hostname}...")

        config = conn.send_command(
            "show running-config",
            read_timeout=60
        )

        filename = f"{backup_folder}/{hostname}.txt"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(config)

        conn.disconnect()

        print(f"{hostname} backup completed")

    except Exception as e:
        print(f"ERROR: {e}")