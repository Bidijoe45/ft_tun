import socket
import signal
import sys
import select
from ipaddress import IPv4Address

from TunInterface import TunInterface

class Client:

    def __init__(self, tun_int_name: str, tun_int_ip: IPv4Address, remote_ip: IPv4Address):
        signal.signal(signal.SIGINT, self.signal_handler)
        self.tun_tap_int: TunInterface = TunInterface(tun_int_name, IPv4Address(tun_int_ip))
        self.remote_ip: IPv4Address = remote_ip
        self.running: bool = True
        self.poll: select.poll = select.poll()
        self.server_sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_sock.bind(("0.0.0.0", 3000))
        self.server_sock.setblocking(False)

    def signal_handler(self, sig, frame) -> None:
        self.running = False

    def register_poll(self) -> None:
        self.poll.register(self.tun_tap_int.fd, select.POLLIN | select.POLLOUT)
        self.poll.register(self.server_sock, select.POLLIN | select.POLLOUT)

    def poll_loop(self) -> None:

        from_server_buffer: bytes = b''
        from_tun_tap_buffer: bytes = b''

        while self.running:
            ready_fds: list[tuple[int, int]] = self.poll.poll(1000)

            for (fd, event) in ready_fds:
                
                if event & select.POLLIN:
                    if fd == self.server_sock.fileno():
                        from_server_data = self.read_from_server()
                        from_server_buffer += from_server_data
                    if fd == self.tun_tap_int.fd.fileno():  
                        from_tun_tap_buffer += self.tun_tap_int.readall()

                if event & select.POLLOUT:
                    if fd == self.server_sock.fileno() and len(from_tun_tap_buffer) > 0:
                        self.send_to_server(from_tun_tap_buffer)
                        from_tun_tap_buffer = b''
                    if fd == self.tun_tap_int.fd.fileno() and len(from_server_buffer) > 0:
                        self.send_to_tun_tap_int(from_server_buffer)
                        from_server_buffer = b''

    def send_to_server(self, data: bytes) -> None:
        self.server_sock.sendto(data, (self.remote_ip, 3000))

    def read_from_server(self) -> bytes:
        data: bytes = b''

        while True:
            try:
                chunk: bytes = self.server_sock.recv(1024)
                data += chunk
            except:
                break
        return data

    def send_to_tun_tap_int(self, data: bytes) -> None:
        self.tun_tap_int.write(data)

    def run(self) -> None:
        self.register_poll()
        self.poll_loop()

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("usage: python client.py tun-interface-name tun-interface-ip remote-host-ip")
        exit(1)

    client = Client(sys.argv[1], sys.argv[2], sys.argv[3])
    client.run()