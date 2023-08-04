import socket
import select
import sys

class Server:
    def __init__(self, port):
        self.port: int = port
        self.running = True
    
    def run(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", self.port))
        sock.setblocking(False)

        poller = select.poll()
        poller.register(sock, select.POLLIN | select.POLLOUT)

        while self.running:
            ready_fds = poller.poll()

            for (fd, event) in ready_fds:

                if event & select.POLLIN:
                    data = sock.recv(1024)
                    if (len(data) > 0):
                        print(f"DATA: {data}")

                if event & select.POLLOUT:
                    pass


if __name__ == "__main__":
    Server(3000).run();
