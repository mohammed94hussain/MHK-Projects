import pandas as pd
from netmiko import ConnectHandler
import getpass
import time

def get_credentials():
    """Prompt user for username and password."""
    username = input("Enter your username: ")
    password = getpass.getpass()
    return username, password

def read_devices(file_path='IP.xlsx'):
    """Read device IPs and hostnames from an Excel file."""
    try:
        df = pd.read_excel(file_path, header=None, names=['ip', 'hostname'])
        return df.to_dict('records')
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return []
    except Exception as e:
        print(f"An error occurred while reading the Excel file: {e}")
        return []

def get_device_info(handler):
    """Gather and parse device information."""
    data = {}
    data['hostname'] = handler.find_prompt().strip('#>')

    # Get interface description
    output = handler.send_command('show interfaces description', use_textfsm=True)
    data['interfaces'] = output

    # Get interface status
    output = handler.send_command('show interfaces status', use_textfsm=True)
    for i, intf in enumerate(data['interfaces']):
        for status in output:
            if intf['port'] == status['port']:
                data['interfaces'][i].update(status)

    # Get inventory
    output = handler.send_command('show inventory', use_textfsm=True)
    data['inventory'] = output

    # Get CDP neighbors
    output = handler.send_command('show cdp neighbors detail', use_textfsm=True)
    data['cdp_neighbors'] = output

    # Get interface details (for capacity and link time)
    output = handler.send_command('show interfaces', use_textfsm=True)
    for i, intf in enumerate(data['interfaces']):
        for detail in output:
            if intf['port'] == detail['interface']:
                data['interfaces'][i]['last_input'] = detail.get('last_input', 'N/A')
                data['interfaces'][i]['last_output'] = detail.get('last_output', 'N/A')
                data['interfaces'][i]['bandwidth'] = detail.get('bandwidth', 'N/A')

    # Get version (for serials)
    output = handler.send_command('show version', use_textfsm=True)
    data['version'] = output

    return data

def main():
    """Main function to orchestrate the inventory process."""
    username, password = get_credentials()
    devices = read_devices()

    if not devices:
        print("No devices to process. Exiting.")
        return

    all_data = []

    for device in devices:
        device_info = {
            'ip': device['ip'],
            'hostname': device['hostname'],
            'device_type': 'cisco_ios',  # Assuming Cisco IOS devices
            'username': username,
            'password': password,
        }

        try:
            print(f"Connecting to {device['hostname']} ({device['ip']})...")
            with ConnectHandler(**device_info) as handler:
                # Placeholder for data gathering
                data = get_device_info(handler)
                all_data.append(data)
                print(f"Successfully gathered data from {device['hostname']}.")

        except Exception as e:
            print(f"Failed to connect or gather data from {device['hostname']}: {e}")

        finally:
            # Add a 1-minute delay between device logins
            print("Waiting for 1 minute before connecting to the next device...")
            time.sleep(60)

    # Process the collected data into a flat structure for Excel
    if all_data:
        flat_data = []
        for data in all_data:
            device_hostname = data['hostname']
            device_serials = [item['sn'] for item in data.get('inventory', []) if 'Chassis' in item['name']]
            power_supply_serials = [item['sn'] for item in data.get('inventory', []) if 'Power Supply' in item['name']]

            for interface in data.get('interfaces', []):
                port_name = interface.get('port')
                neighbor_info = next((n for n in data.get('cdp_neighbors', []) if n.get('local_port') == port_name), None)

                row = {
                    'Hostname': device_hostname,
                    'IP Address': device['ip'],
                    'Port': port_name,
                    'Description': interface.get('description', 'N/A'),
                    'Status': interface.get('status', 'N/A'),
                    'VLAN': interface.get('vlan', 'N/A'),
                    'Duplex': interface.get('duplex', 'N/A'),
                    'Speed': interface.get('speed', 'N/A'),
                    'Type': interface.get('type', 'N/A'),
                    'Neighbor': neighbor_info.get('neighbor', 'N/A') if neighbor_info else 'N/A',
                    'Neighbor IP': neighbor_info.get('neighbor_ip', 'N/A') if neighbor_info else 'N/A',
                    'Neighbor Platform': neighbor_info.get('platform', 'N/A') if neighbor_info else 'N/A',
                    'Last Input': interface.get('last_input', 'N/A'),
                    'Last Output': interface.get('last_output', 'N/A'),
                    'Bandwidth': interface.get('bandwidth', 'N/A'),
                    'Device Serial': ', '.join(device_serials),
                    'Power Supply Serials': ', '.join(power_supply_serials),
                    'RX Transceiver': 'N/A' # Placeholder, as this info is not typically in these commands
                }
                flat_data.append(row)

        df = pd.DataFrame(flat_data)
        df.to_excel('cisco_device_database.xlsx', index=False)
        print("Inventory data has been successfully saved to cisco_device_database.xlsx")
    else:
        print("No data was collected.")

if __name__ == "__main__":
    main()