import getpass
import time
import re
from netmiko import ConnectHandler
from openpyxl import Workbook, load_workbook
import sys

# --- Prompt for username and password (using getpass for security) ---
print("--- Authentication ---")
username = input("Enter your username: ")
password = getpass.getpass()
print("----------------------")

# Read IP addresses from IP.xlsx
try:
    wb_ip = load_workbook('IP.xlsx')
    sheet_ip = wb_ip.active
    ips = [cell.value for cell in sheet_ip['A'][1:] if cell.value]
except FileNotFoundError:
    print("Error: IP.xlsx not found. Please create it and add IP addresses in column A, starting from row 2.")
    sys.exit(1)

# Create a new workbook for the output
wb_db = Workbook()
sheet_db = wb_db.active
sheet_db.title = "DataBase"

# Write headers to the output file
headers = [
    "Hostname", "IP", "Port", "Description", "Status", "VLAN",
    "Neighbor", "Port Speed", "Link Uptime", "Device Serial",
    "Power Supply Serials", "Transceiver Info", "Port Serial", "Rx Power (dBm)"
]
sheet_db.append(headers)

# Loop through each IP address
for ip in ips:
    print(f"\n🚀 Connecting to {ip}...")
    device = {
        'device_type': 'cisco_ios',
        'host': ip,
        'username': username,
        'password': password,
        'conn_timeout': 60,
        'auth_timeout': 60,
        'global_delay_factor': 2,
    }

    try:
        net_connect = ConnectHandler(**device)
        hostname = net_connect.find_prompt()[:-1]
        print(f"✅ Successfully logged in and prompt found: {hostname}")

        # Get inventory for serials
        show_inventory_raw = net_connect.send_command('show inventory', use_textfsm=False)
        device_serial = "N/A"
        power_supply_serials = []
        transceivers = {}

        chassis_match = re.search(r'NAME: "Chassis.*", DESCR: ".*"\nPID: .*, VID: .*, SN: (\S+)', show_inventory_raw)
        if chassis_match:
            device_serial = chassis_match.group(1)

        for match in re.finditer(r'NAME: "Power Supply Module \d+", DESCR: ".*"\nPID: .*, VID: .*, SN: (\S+)', show_inventory_raw):
            power_supply_serials.append(match.group(1))

        for match in re.finditer(r'NAME: "(\S+Ethernet\S+)", DESCR: ".*"\nPID: (\S+)\s+, VID: \S+\s+, SN: (\S+)', show_inventory_raw):
            port_name, pid, sn = match.groups()
            transceivers[port_name] = {"type": pid, "sn": sn}

        # Get base interface status
        show_int_status = net_connect.send_command('show interfaces status', use_textfsm=True)

        # Get CDP Neighbors
        show_cdp_neighbors = net_connect.send_command('show cdp neighbor detail', use_textfsm=True)
        cdp_neighbors = {n['local_port']: n['destination_host'] for n in show_cdp_neighbors}

        # Get interface descriptions
        show_int_desc = net_connect.send_command('show interfaces description', use_textfsm=True)
        descriptions = {item['port']: item['desc'] for item in show_int_desc}

        # Get Link Uptime
        show_link = net_connect.send_command('show interface link', use_textfsm=True)
        interface_uptimes = {iface['interface']: iface.get('link_uptime', 'N/A') for iface in show_link}

        # Get Transceiver Rx Power
        show_transceiver = net_connect.send_command('show interface transceiver', use_textfsm=True)
        rx_powers = {item['port']: item.get('receive_pwr', 'N/A') for item in show_transceiver}

        # Process each interface
        for interface in show_int_status:
            port = interface.get('port', 'N/A')

            description = descriptions.get(port, 'N/A')
            status = interface.get('status', 'N/A')
            vlan = interface.get('vlan', 'N/A')
            neighbor = cdp_neighbors.get(port, 'N/A')
            port_speed = interface.get('speed', 'N/A')
            link_uptime = interface_uptimes.get(port, 'N/A')

            transceiver_details = transceivers.get(port, {})
            transceiver_type = transceiver_details.get('type', 'N/A')
            port_serial = transceiver_details.get('sn', 'N/A')
            transceiver_info = f"Type: {transceiver_type}, SN: {port_serial}" if port_serial != 'N/A' else 'N/A'
            rx_power = rx_powers.get(port, 'N/A')

            row_data = [
                hostname, ip, port, description, status, vlan,
                neighbor, port_speed, link_uptime, device_serial,
                ", ".join(power_supply_serials), transceiver_info, port_serial, rx_power
            ]
            sheet_db.append(row_data)

        net_connect.disconnect()
        print(f"✅ Successfully collected data from {ip}")

    except Exception as e:
        error_type = "AUTHENTICATION FAILED" if "Authentication" in str(e) else "COMMAND FAILED"
        print(f"❌ Failure on {ip}: {e}")
        sheet_db.append([hostname if 'hostname' in locals() else 'N/A', ip, f"{error_type}: {str(e).splitlines()[0]}", "", "", "", "", "", "", "", "", "", ""])

    print("⏳ Waiting for 10 seconds...")
    time.sleep(10)

# Save the workbook
wb_db.save('DataBase.xlsx')

print("\n--- Script finished. Data saved to DataBase.xlsx ---")
