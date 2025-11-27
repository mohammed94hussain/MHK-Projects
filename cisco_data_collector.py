
import getpass
import time
import re
from netmiko import ConnectHandler
from openpyxl import Workbook, load_workbook

# Prompt for username and password
username = input("Enter your username: ")
password = getpass.getpass()

# Read IP addresses from IP.xlsx
try:
    wb_ip = load_workbook('IP.xlsx')
    sheet_ip = wb_ip.active
    ips = [cell.value for cell in sheet_ip['A'][1:] if cell.value]
except FileNotFoundError:
    print("Error: IP.xlsx not found. Please create it and add IP addresses in column A, starting from row 2.")
    exit()

# Create a new workbook for the output
wb_db = Workbook()
sheet_db = wb_db.active
sheet_db.title = "DataBase"

# Write headers to the output file
headers = [
    "Hostname", "IP", "Port", "Description", "Status", "VLAN",
    "Neighbor", "Port Speed", "Link Uptime", "Device Serial",
    "Power Supply Serials", "Transceiver Info", "Port Serial"
]
sheet_db.append(headers)


# Loop through each IP address
for ip in ips:
    print(f"Connecting to {ip}...")
    device = {
        'device_type': 'cisco_ios',
        'host': ip,
        'username': username,
        'password': password,
    }
    hostname = "N/A"

    try:
        net_connect = ConnectHandler(**device)
        net_connect.enable()

        # Get hostname
        hostname = net_connect.find_prompt()[:-1]

        # Get inventory, including transceivers
        show_inventory_raw = net_connect.send_command('show inventory', use_textfsm=False)
        device_serial = "N/A"
        power_supply_serials = []
        transceivers = {}

        # Parse chassis serial
        chassis_match = re.search(r'NAME: "Chassis.*", DESCR: ".*"\nPID: .*, VID: .*, SN: (\S+)', show_inventory_raw)
        if chassis_match:
            device_serial = chassis_match.group(1)

        # Parse power supply serials
        for match in re.finditer(r'NAME: "Power Supply Module \d+", DESCR: ".*"\nPID: .*, VID: .*, SN: (\S+)', show_inventory_raw):
            power_supply_serials.append(match.group(1))

        # Parse transceiver serials and info from inventory
        for match in re.finditer(r'NAME: "(\S+)", DESCR: "(\S+)"\nPID: (\S+)\s+, VID: \S+\s+, SN: (\S+)', show_inventory_raw):
            port_name, descr, pid, sn = match
            if "transceiver" in descr.lower() or "sfp" in descr.lower():
                 transceivers[port_name] = f"Type: {pid}, SN: {sn}"


        # Get interface status
        show_int_status = net_connect.send_command('show interfaces status', use_textfsm=True)

        # Get LLDP neighbors
        show_lldp_neighbors = net_connect.send_command('show lldp neighbors detail', use_textfsm=True)
        neighbors = {n['local_interface']: n.get('neighbor_system_name', 'N/A') for n in show_lldp_neighbors}

        # Get interface descriptions
        show_int_desc = net_connect.send_command('show interfaces description', use_textfsm=True)
        descriptions = {item['port']: item['desc'] for item in show_int_desc}

        # Get interface uptime from raw output
        show_interfaces_raw = net_connect.send_command('show interfaces', use_textfsm=False)
        interface_uptimes = {}
        # Simple regex to find "Last link flapped..."
        for match in re.finditer(r'(\S+ is .*?)\n(?:.|\n)*?Last link flapped (\S+)', show_interfaces_raw):
            interface_name = match.group(1).split()[0]
            uptime = match.group(2)
            interface_uptimes[interface_name] = uptime

        # Process each interface
        for interface in show_int_status:
            port = interface['port']
            description = descriptions.get(port, 'N/A')
            status = interface['status']
            vlan = interface['vlan']
            neighbor = neighbors.get(port, 'N/A')
            port_speed = interface.get('speed', 'N/A')
            link_uptime = interface_uptimes.get(port, 'N/A')
            transceiver_info = transceivers.get(port, 'N/A')
            port_serial = transceiver_info.split('SN: ')[1] if 'SN: ' in transceiver_info else 'N/A'


            row_data = [
                hostname, ip, port, description, status, vlan,
                neighbor, port_speed, link_uptime, device_serial,
                ", ".join(power_supply_serials), transceiver_info, port_serial
            ]
            sheet_db.append(row_data)

        net_connect.disconnect()
        print(f"Successfully collected data from {ip}")

    except Exception as e:
        print(f"Failed to connect to {ip}: {e}")
        sheet_db.append([hostname, ip, "CONNECTION FAILED", str(e), "", "", "", "", "", "", "", ""])

    # Wait for 30 seconds
    print("Waiting for 30 seconds...")
    time.sleep(30)

# Save the workbook
wb_db.save('DataBase.xlsx')

print("Script finished. Data saved to DataBase.xlsx")
