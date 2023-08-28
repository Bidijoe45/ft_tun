from ipaddress import IPv4Address
import struct
from enum import Enum
import io
import fcntl
import os

class TunInterface:

    def __init__(self, name: str, ip: IPv4Address):
        self.name: str = name
        self.ip: IPv4Address = ip
        self.type: self.Type = type
        self.fd: io.FileIO = self.__open()
        os.set_blocking(self.fd.fileno(), False)

    def __open(self) -> io.FileIO:
        tun = open("/dev/net/tun", "r+b", buffering=0)
        LINUX_IFF_TUN = 0x0001
        LINUX_IFF_NO_PI = 0x1000
        LINUX_TUNSETIFF = 0x400454CA
        flags = LINUX_IFF_TUN | LINUX_IFF_NO_PI
        ifs = struct.pack("16sH22s", self.name.encode("utf-8"), flags, b"")
        fcntl.ioctl(tun, LINUX_TUNSETIFF, ifs)
        return tun

    def readall(self) -> bytes:
        data = self.fd.readall()
        return data

    def write(self, data):
        self.fd.write(data)

    def close(self):
        self.fd.close()