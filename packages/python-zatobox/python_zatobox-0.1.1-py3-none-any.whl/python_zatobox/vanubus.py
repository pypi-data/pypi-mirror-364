

import socket

from zeroconf import ServiceBrowser, ServiceListener, Zeroconf

import time

import struct

class InputRegMainMeter:
    def __init__(self):
        self.power = 0.0
        self.energy_import = 0.0
        self.energy_export = 0.0
        self.power_1 = 0.0
        self.power_2 = 0.0
        self.power_3 = 0.0
        self.voltage_1 = 0.0
        self.voltage_2 = 0.0
        self.voltage_3 = 0.0
        self.voltage_U12 = 0.0
        self.voltage_U23 = 0.0
        self.voltage_U31 = 0.0
        self.current_1 = 0.0
        self.current_2 = 0.0
        self.current_3 = 0.0
        self.pf_1 = 0.0
        self.pf_2 = 0.0
        self.pf_3 = 0.0
        self.frequency = 0.0
        self.reserve1 = 0.0 
        self.reserve2 = 0.0 
        self.reserve3 = 0.0 
        self.reserve4 = 0.0 
        self.reserve5 = 0.0 
        self.reserve6 = 0.0 
        self.reserve7 = 0.0 
        self.reserve8 = 0.0 
        self.reserve9 = 0.0 
        self.reserve10 = 0.0 
        self.reserve11 = 0.0 
        self.attributes = [
            'power', 'energy_import', 'energy_export', 'power_1', 'power_2', 'power_3',
            'voltage_1', 'voltage_2', 'voltage_3', 'voltage_U12', 'voltage_U23', 'voltage_U31',
            'current_1', 'current_2', 'current_3', 'pf_1', 'pf_2', 'pf_3', 'frequency',
            'reserve1', 'reserve2', 'reserve3', 'reserve4', 'reserve5', 'reserve6', 'reserve7', 
            'reserve8', 'reserve9', 'reserve10', 'reserve11', 
        ]
class InputRegGasMeter:
    def __init__(self):
        self.energy = 0.0
        self.reserve1 = 0.0
        self.reserve2 = 0.0
        self.reserve3 = 0.0
        self.reserve4 = 0.0
        self.reserve5 = 0.0
        self.reserve6 = 0.0
        self.reserve7 = 0.0
        self.reserve8 = 0.0
        self.reserve9 = 0.0
        self.reserve10 = 0.0
        self.reserve11 = 0.0
        self.reserve12 = 0.0
        self.reserve13 = 0.0
        self.reserve14 = 0.0
        self.reserve15 = 0.0
        self.reserve16 = 0.0
        self.reserve17 = 0.0
        self.reserve18 = 0.0
        self.reserve19 = 0.0
        self.reserve20 = 0.0
        self.reserve21 = 0.0
        self.reserve22 = 0.0
        self.reserve23 = 0.0
        self.reserve24 = 0.0
        self.reserve25 = 0.0
        self.reserve26 = 0.0
        self.reserve27 = 0.0
        self.reserve28 = 0.0
        self.reserve29 = 0.0
        # Attribute list for InputRegGM
        self.attributes = [
            'energy',
            'reserve1', 'reserve2', 'reserve3', 'reserve4', 'reserve5',
            'reserve6', 'reserve7', 'reserve8', 'reserve9', 'reserve10',
            'reserve11', 'reserve12', 'reserve13', 'reserve14', 'reserve15',
            'reserve16', 'reserve17', 'reserve18', 'reserve19', 'reserve20',
            'reserve21', 'reserve22', 'reserve23', 'reserve24', 'reserve25',
            'reserve26', 'reserve27', 'reserve28', 'reserve29'
        ]


class InputRegPV:
    def __init__(self):
        self.power = 0.0
        self.energy = 0.0
        self.reserve1 = 0.0
        self.reserve2 = 0.0
        self.reserve3 = 0.0
        self.reserve4 = 0.0
        self.reserve5 = 0.0
        self.reserve6 = 0.0
        self.reserve7 = 0.0
        self.reserve8 = 0.0
        self.reserve9 = 0.0
        self.reserve10 = 0.0
        self.reserve11 = 0.0
        self.reserve12 = 0.0
        self.reserve13 = 0.0
        self.reserve14 = 0.0
        self.reserve15 = 0.0
        self.reserve16 = 0.0
        self.reserve17 = 0.0
        self.reserve18 = 0.0
        self.reserve19 = 0.0
        self.reserve20 = 0.0
        self.reserve21 = 0.0
        self.reserve22 = 0.0
        self.reserve23 = 0.0
        self.reserve24 = 0.0
        self.reserve25 = 0.0
        self.reserve26 = 0.0
        self.reserve27 = 0.0
        self.reserve28 = 0.0
        # Attribute list for InputRegPV
        self.attributes = [
            'power', 'energy',
            'reserve1', 'reserve2', 'reserve3', 'reserve4', 'reserve5',
            'reserve6', 'reserve7', 'reserve8', 'reserve9', 'reserve10',
            'reserve11', 'reserve12', 'reserve13', 'reserve14', 'reserve15',
            'reserve16', 'reserve17', 'reserve18', 'reserve19', 'reserve20',
            'reserve21', 'reserve22', 'reserve23', 'reserve24', 'reserve25',
            'reserve26', 'reserve27', 'reserve28'
        ]


class InputRegBattery:
    def __init__(self):
        self.power = 0.0
        self.energy_charge = 0.0
        self.energy_discharge = 0.0
        self.soc = 0.0
        self.reserve1 = 0.0
        self.reserve2 = 0.0
        self.reserve3 = 0.0
        self.reserve4 = 0.0
        self.reserve5 = 0.0
        self.reserve6 = 0.0
        self.reserve7 = 0.0
        self.reserve8 = 0.0
        self.reserve9 = 0.0
        self.reserve10 = 0.0
        self.reserve11 = 0.0
        self.reserve12 = 0.0
        self.reserve13 = 0.0
        self.reserve14 = 0.0
        self.reserve15 = 0.0
        self.reserve16 = 0.0
        self.reserve17 = 0.0
        self.reserve18 = 0.0
        self.reserve19 = 0.0
        self.reserve20 = 0.0
        self.reserve21 = 0.0
        self.reserve22 = 0.0
        self.reserve23 = 0.0
        self.reserve24 = 0.0
        self.reserve25 = 0.0
        self.reserve26 = 0.0
        # Attribute list for InputRegBA
        self.attributes = [
            'power', 'energy_charge', 'energy_discharge', 'soc',
            'reserve1', 'reserve2', 'reserve3', 'reserve4', 'reserve5',
            'reserve6', 'reserve7', 'reserve8', 'reserve9', 'reserve10',
            'reserve11', 'reserve12', 'reserve13', 'reserve14', 'reserve15',
            'reserve16', 'reserve17', 'reserve18', 'reserve19', 'reserve20',
            'reserve21', 'reserve22', 'reserve23', 'reserve24', 'reserve25',
            'reserve26'
        ]

class InputRegUsage:
    def __init__(self):
        self.power = 0.0
        self.energy = 0.0
        self.reserve1 = 0.0
        self.reserve2 = 0.0
        self.reserve3 = 0.0
        self.reserve4 = 0.0
        self.reserve5 = 0.0
        self.reserve6 = 0.0
        self.reserve7 = 0.0
        self.reserve8 = 0.0
        self.reserve9 = 0.0
        self.reserve10 = 0.0
        self.reserve11 = 0.0
        self.reserve12 = 0.0
        self.reserve13 = 0.0
        self.reserve14 = 0.0
        self.reserve15 = 0.0
        self.reserve16 = 0.0
        self.reserve17 = 0.0
        self.reserve18 = 0.0
        self.reserve19 = 0.0
        self.reserve20 = 0.0
        self.reserve21 = 0.0
        self.reserve22 = 0.0
        self.reserve23 = 0.0
        self.reserve24 = 0.0
        self.reserve25 = 0.0
        self.reserve26 = 0.0
        self.reserve27 = 0.0
        self.reserve28 = 0.0
        # Attribute list for InputRegUS
        self.attributes = [
            'power', 'energy',
            'reserve1', 'reserve2', 'reserve3', 'reserve4', 'reserve5',
            'reserve6', 'reserve7', 'reserve8', 'reserve9', 'reserve10',
            'reserve11', 'reserve12', 'reserve13', 'reserve14', 'reserve15',
            'reserve16', 'reserve17', 'reserve18', 'reserve19', 'reserve20',
            'reserve21', 'reserve22', 'reserve23', 'reserve24', 'reserve25',
            'reserve26', 'reserve27', 'reserve28'
        ]

class InputRegCharger:
    def __init__(self):
        self.power = 0.0
        self.energy = 0.0
        self.soc = 0.0
        self.reserve1 = 0.0
        self.reserve2 = 0.0
        self.reserve3 = 0.0
        self.reserve4 = 0.0
        self.reserve5 = 0.0
        self.reserve6 = 0.0
        self.reserve7 = 0.0
        self.reserve8 = 0.0
        self.reserve9 = 0.0
        self.reserve10 = 0.0
        self.reserve11 = 0.0
        self.reserve12 = 0.0
        self.reserve13 = 0.0
        self.reserve14 = 0.0
        self.reserve15 = 0.0
        self.reserve16 = 0.0
        self.reserve17 = 0.0
        self.reserve18 = 0.0
        self.reserve19 = 0.0
        self.reserve20 = 0.0
        self.reserve21 = 0.0
        self.reserve22 = 0.0
        self.reserve23 = 0.0
        self.reserve24 = 0.0
        self.reserve25 = 0.0
        self.reserve26 = 0.0
        self.reserve27 = 0.0

        # Attribute list for InputRegCH
        self.attributes = [
            'power', 'energy', 'soc',
            'reserve1', 'reserve2', 'reserve3', 'reserve4', 'reserve5',
            'reserve6', 'reserve7', 'reserve8', 'reserve9', 'reserve10',
            'reserve11', 'reserve12', 'reserve13', 'reserve14', 'reserve15',
            'reserve16', 'reserve17', 'reserve18', 'reserve19', 'reserve20',
            'reserve21', 'reserve22', 'reserve23', 'reserve24', 'reserve25',
            'reserve26', 'reserve27'
        ]



class SensorData:


    

    def __init__(self, data: bytes) -> None:
    
        # Decode the bytes using little-endian byte order
        decoded_value = int.from_bytes( data[0:4], byteorder='little')

        # SE_TYPE__sensor_type_unspecified = 0
        # SE_TYPE__mainmeter = 1
        # SE_TYPE__gasmeter = 2
        # SE_TYPE__pv = 3
        # SE_TYPE__battery = 4
        # SE_TYPE__usage = 5
        # SE_TYPE__charger = 6
        # SE_TYPE__forecast = 7 #not use here
        # SE_TYPE__marketprice = 8 #not use here

        match decoded_value:
            case 1:
                input_reg = InputRegMainMeter()
            case 2:
                input_reg = InputRegGasMeter()
            case 3:
                input_reg = InputRegPV()
            case 4:
                input_reg = InputRegBattery()
            case 5:
                input_reg = InputRegUsage()
            case 6:
                input_reg = InputRegCharger()



        for i in range(30):

            # Decode the bytes using little-endian byte order
            decoded_value = int.from_bytes( data[(i+1)*4:(i+2)*4], byteorder='little')

            # Convert the integer value to a float
            float_value = struct.unpack('f', struct.pack('I', decoded_value))[0]
                        
            setattr(input_reg, input_reg.attributes[i], float_value)

        
        self.data = input_reg




class Vanubus:
    def __init__(self, host, port=3333) -> None:
        isipadress : bool = False
        try:
            socket.inet_aton(host)
            # legal
            isipadress = True
        except socket.error:
            # Not legal
            isipadress = False

        if (isipadress):
            self.ip_address = host
            self.port = port
        else:
            try:
                ip = socket.gethostbyname(host)
                print(f"{host} resolved to {ip}")
                self.ip_address = ip
            except socket.gaierror:
                print(f"Could not resolve {host}")
        
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def setipadress(self, ipadress):
        self.ip_address = ipadress

    def discover(self, timeout = 3) -> list:

        zeroconf = Zeroconf()
        listener = self._MyListener()
        browser = ServiceBrowser(zeroconf, "_vanubus._tcp.local.", listener)

        waittime = 0
        while(waittime < timeout):            
            time.sleep(0.1)
            waittime = waittime + 0.1
        
        zeroconf.close()

        return listener.services

    def getdata(self, sensorids = []) -> list:
        if (not(self._is_connected())):
            connected = self._connect()
            if (not(connected)):
                return 

        # Create tx_buffer of 64 bytes, initialized with zeros
        tx_buffer = bytearray(64)

        # Set id for request
        tx_buffer[0] = 1

        # Fill the buffer with client ids, starting at index 1
        for i in range(len(sensorids)):
            tx_buffer[i + 1] = sensorids[i]  # or clientdata[i].id if objects

        # Send the buffer minus the last byte (63 bytes)
        try:
            sent_bytes = self.tcp_socket.send(tx_buffer[:63])
        except socket.error as e:
            print(f"Socket send error: {e}")


        try:
            while True:
                data = self.tcp_socket.recv(1024)
                if data:
                    return self._decode_rx_buffer(data, 1)
                time.sleep(1)
        except Exception as e:
            print(f"Error receiving data: {e}")

        return []

    def _decode_rx_buffer(self,  data : bytes, type) -> list:
        hex_representation = data.hex()

        
        match type:
            case 1:
                sensors = []
                sensorsearch = True
                position = 0
                sensordataelength = (30*4 + 4)
                sensorlength = (len(data))/(sensordataelength)
                for i in range(round(sensorlength)):
                    sensorbytes = data[sensordataelength*i:sensordataelength*(i+1)]
                    sensor = SensorData(sensorbytes)
                    
                    sensors.append(sensor)
                return sensors
            case 2:
                return "two"

    def _is_connected(self) -> bool:
        try:
            # Check if socket is closed
            self.tcp_socket.getpeername()  # Raises error if not connected
        except socket.error:
            return False
        return True
    
    def _connect(self) -> bool:
        try:
            self.tcp_socket.connect((self.ip_address, self.port))
            print(f"Connected to {self.ip_address} on port {self.port}")
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
        
        return False


    def _listen(self):
        try:
            while True:
                data = self.tcp_socket.recv(1024)
                if not data:
                    break
                print(f"Received data: {data.decode('utf-8')}")
        except Exception as e:
            print(f"Error receiving data: {e}")
        finally:
            self.close()

    def _close(self):
        print("Closing socket")
        self.tcp_socket.close()

    class _MyListener(ServiceListener):
        def __init__(self):
            self.services = []

        def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
            print(f"Service {name} updated")

        def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
            print(f"Service {name} removed")

        def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
            info = zc.get_service_info(type_, name)
            if info:
                ip = ".".join(map(str, info.addresses[0]))
                splitname = name.split('.')
                service_data = {
                    "name": splitname[0],
                    "ip": ip,
                    "port": info.port,
                    "properties": info.properties
                }
                self.services.append(service_data)


# Example usage
if __name__ == "__main__":
    host = "192.168.68.102"  # Replace with the actual IP address of the device
    client = Vanubus(host)

    test = client.discover()
    print(test)

    sensordata  = client.getdata([1,2,6])
    print(sensordata)