from netmiko import ConnectHandler

devices = [
    {"device_type": "cisco_ios_telnet", "host": "192.168.20.128", "port": 5002},
    {"device_type": "cisco_ios_telnet", "host": "192.168.20.128", "port": 5004},
    {"device_type": "cisco_ios_telnet", "host": "192.168.20.128", "port": 5008},
]

config_commands = [
    
    "service password-encryption"
]

banner_command = """
banner motd #
****************************************
AUTHORIZED ACCESS ONLY
****************************************
#
"""

for device in devices:
    try:
        conn = ConnectHandler(**device)
        conn.enable()

        hostname = conn.find_prompt().rstrip("#>").strip()

        print(f"Deploying to {hostname}")
        conn.send_config_set(banner_command.splitlines())

        output = conn.send_config_set(config_commands)

        print(output)

        conn.save_config()

        conn.disconnect()

        print(f"{hostname} SUCCESS\n")

    except Exception as e:
        print(f"FAILED: {e}")