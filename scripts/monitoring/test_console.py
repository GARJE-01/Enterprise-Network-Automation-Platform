from netmiko import ConnectHandler

device = {
    "device_type": "cisco_ios_telnet",
    "host": "192.168.20.128",
    "port": 5002,
}

conn = ConnectHandler(**device)

print(conn.find_prompt())

conn.disconnect()