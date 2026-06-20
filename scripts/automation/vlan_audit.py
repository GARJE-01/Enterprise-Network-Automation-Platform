from netmiko import ConnectHandler

switches = [
    {"device_type":"cisco_ios_telnet","host":"192.168.20.128","port":5000},
    {"device_type":"cisco_ios_telnet","host":"192.168.20.128","port":5006},
]

for switch in switches:

    conn = ConnectHandler(**switch)
    conn.enable()

    hostname = conn.find_prompt().rstrip("#>").strip()

    print(f"\n{hostname}")
    print("="*40)

    output = conn.send_command("show vlan brief")

    print(output)

    conn.disconnect()