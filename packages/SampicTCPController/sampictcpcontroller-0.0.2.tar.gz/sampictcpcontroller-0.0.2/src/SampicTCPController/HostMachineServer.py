import socket


class HostMachineServer:
    _socket = None

    def __init__(self, port=4242):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind(("127.0.0.1", port))

    def loop(self):
        conn, addr = self._socket.accept
        with conn:
            print(f"New client connected: {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print(f"Received {data} from {addr}")
