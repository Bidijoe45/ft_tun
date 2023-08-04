import struct
import fcntl
import io
import select
import socket
import time
import subprocess
import signal
from enum import Enum
from ipaddress import IPv4Interface

class TunTapInterface:

    class Type(Enum):
        TUN = 0,
        TAP = 1

    def __init__(self, name: str, ip: IPv4Interface, type: Type):
        self.name: str = name
        self.ip: IPv4Interface = ip
        self.type: self.Type = type
        #self.__create()
        self.fd: io.FileIO = self.__open()

    '''
    def __del__(self):
        print("Destructor!")
        #self.__close()
        #self.__destroy()

    def __create(self):
        subprocess.run(f"ip tuntap add {self.name} mode {self.type.name.lower()}", shell=True)
        subprocess.run(f"ip address add {self.ip.with_prefixlen} def {self.name}", shell=True)
        subprocess.run(f"ip link set {self.name} up", shell=True)
    
    def __destroy(self):
        subprocess.run(f"ip link delete {self.name}", shell=True)
    '''

    def __open(self) -> io.FileIO:
        tun = open("/dev/net/tun", "r+b", buffering=0)
        LINUX_IFF_TUN = 0x0001
        LINUX_IFF_NO_PI = 0x1000
        LINUX_TUNSETIFF = 0x400454CA
        flags = LINUX_IFF_TUN | LINUX_IFF_NO_PI
        ifs = struct.pack("16sH22s", self.name.encode("utf-8"), flags, b"")
        fcntl.ioctl(tun, LINUX_TUNSETIFF, ifs)
        return tun
    
    #TODO: FD has no close? WTF
    #def __close(self):
    #    self.fd.close()

    def read(self, bytes: int) -> str:
        return self.fd.read(bytes)

    def write(self, data):
        self.fd.write(data)

    def close(self):
        self.fd.close()

class Client:

    def __init__(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        self.tun_tap_int: TunTapInterface = TunTapInterface("tun0", IPv4Interface("10.0.0.2/24"), TunTapInterface.Type.TUN)
        self.running = True
        self.poll = select.poll()
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def signal_handler(self, sig, frame):
        self.running = False

    def register_poll(self) -> None:
        self.poll.register(self.tun_tap_int.fd, select.POLLIN | select.POLLOUT)

    def poll_loop(self) -> None:
        while self.running:
            ready_fds = self.poll.poll(1000)

            for (fd, event) in ready_fds:
                if event & select.POLLIN:
                    data = self.tun_tap_int.read(1024)
                    if (len(data) > 0):
                        print(f"DATA: {data}")
                        self.send_to_server(data)
                if event & select.POLLOUT:
                    pass

    def send_to_server(self, data):
        self.server_sock.sendto(data, ("172.23.0.3", 3000))

    def run(self):
        self.register_poll()
        self.poll_loop()


if __name__ == "__main__":
    client = Client()
    client.run()