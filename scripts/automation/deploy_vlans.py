from netmiko import ConnectHandler

switches = [
    {
        "device_type": "cisco_ios_telnet",
        "host": "192.168.20.128",
        "port": 5000,
    },
    {
        "device_type": "cisco_ios_telnet",
        "host": "192.168.20.128",
        "port": 5006,
    }
]

config_commands = [
    "vlan 10",
    "name USERS",

    "vlan 20",
    "name SERVERS",

    "vlan 99",
    "name MGMT"
]

for switch in switches:

    try:
        conn = ConnectHandler(**switch)
        conn.enable()

        hostname = conn.find_prompt().rstrip("#>").strip()

        print(f"\nDeploying VLANs to {hostname}")

        output = conn.send_config_set(config_commands)

        print(output)

        conn.save_config()

        conn.disconnect()

        print(f"{hostname} SUCCESS")

    except Exception as e:
        print(f"ERROR: {e}")