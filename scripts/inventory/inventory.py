from netmiko import ConnectHandler

devices = [
    {
        "device_type": "cisco_ios_telnet",
        "host": "192.168.20.128",
        "port": 5002,
    },
    {
        "device_type": "cisco_ios_telnet",
        "host": "192.168.20.128",
        "port": 5004,
    },
    {
        "device_type": "cisco_ios_telnet",
        "host": "192.168.20.128",
        "port": 5008,
    }
]

for device in devices:
    print(f"\nConnecting to port {device['port']}")

    try:
        conn = ConnectHandler(**device)
        conn.enable()

        hostname = conn.find_prompt().rstrip("#>").strip()

        print(f"Connected to {hostname}")

        output = conn.send_command("show ip interface brief")

        with open(f"{hostname}_inventory.txt", "w") as f:
            f.write(output)

        conn.disconnect()

        print("SUCCESS")

    except Exception as e:
        print(f"FAILED: {e}")