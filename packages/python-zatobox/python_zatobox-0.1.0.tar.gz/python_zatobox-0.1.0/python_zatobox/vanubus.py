

import socket

class TCPClient:
    def __init__(self, ip_address, port=3333) -> None:
        self.ip_address = ip_address
        self.port = port
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        try:
            self.tcp_socket.connect((self.ip_address, self.port))
            print(f"Connected to {self.ip_address} on port {self.port}")
        except Exception as e:
            print(f"Failed to connect: {e}")

    def listen(self):
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

    def close(self):
        print("Closing socket")
        self.tcp_socket.close()

# Example usage
if __name__ == "__main__":
    ip_address = "127.0.0.1"  # Replace with the actual IP address of the device
    client = TCPClient(ip_address)
    client.connect()
    client.listen()