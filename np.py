import socket
import threading
import time
import asyncio

# Porta del Proxy
proxyport = int(input('¿QUÉ PUERTO DESEA UTILIZAR (ASEGÚRESE DE QUE NO ESTÉ EN USO)? '))

# CONFIGURACIÓN
LISTENING_ADDR = '0.0.0.0'
LISTENING_PORT = proxyport

PASS = ''

# CONSTANTES
BUFLEN = 4096 * 4
TIMEOUT = 60
DEFAULT_HOST = '127.0.0.1:22'
RESPONSE = 'HTTP/1.1 101 <strong><font color="#2aa2e8">Sky</font><font color="#2cf62e">netw</font><font color="#2aa2e8">orks</font></strong>\r\nContent-length: 0r\n\r\nHTTP/1.1 101 Protocol Acces\r\n\r\n'

class Server(threading.Thread):
    def __init__(self, host, port):
        super().__init__()
        self.running = False
        self.host = host
        self.port = port
        self.connections = []
        self.log_lock = threading.Lock()

    def run(self):
        self.soc = socket.socket(socket.AF_INET)
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.soc.bind((self.host, self.port))
        self.soc.listen(0)
        self.running = True

        try:
            while self.running:
                c, addr = self.soc.accept()
                c.setblocking(1)
                conn = ConnectionHandler(c, self, addr)
                conn.start()
                self.add_connection(conn)
        finally:
            self.running = False
            self.soc.close()

    def print_log(self, log):
        with self.log_lock:
            print(log)

    def add_connection(self, conn):
        self.connections.append(conn)

    def remove_connection(self, conn):
        self.connections.remove(conn)

    def close(self):
        self.running = False
        for conn in self.connections:
            conn.close()

class ConnectionHandler(threading.Thread):
    def __init__(self, client_socket, server, addr):
        super().__init__()
        self.client_socket = client_socket
        self.server = server
        self.addr = addr
        self.target_socket = None

    def close(self):
        if self.client_socket:
            self.client_socket.close()
        if self.target_socket:
            self.target_socket.close()

    async def run(self):
        try:
            data = await self.client_socket.recv(BUFLEN)
            host_port = self.find_header(data, 'X-Real-Host')

            if not host_port:
                host_port = DEFAULT_HOST

            split = self.find_header(data, 'X-Split')

            if split:
                await self.client_socket.recv(BUFLEN)

            if host_port:
                passwd = self.find_header(data, 'X-Pass')

                if PASS and passwd == PASS:
                    await self.method_CONNECT(host_port)
                elif PASS and passwd != PASS:
                    await self.client_socket.send('HTTP/1.1 400 Erroneo By Skynet!\r\n\r\n'.encode())
                elif host_port.startswith('127.0.0.1') or host_port.startswith('localhost'):
                    await self.method_CONNECT(host_port)
                else:
                    await self.client_socket.send('HTTP/1.1 403 Forbidden!\r\n\r\n'.encode())
            else:
                self.server.print_log('- No X-Real-Host!')
                await self.client_socket.send('HTTP/1.1 400 NoXRealHost!\r\n\r\n'.encode())
        except Exception as e:
            self.server.print_log(f'Connection error: {str(e)}')
        finally:
            self.close()
            self.server.remove_connection(self)

    async def method_CONNECT(self, path):
        self.server.print_log(f'CONNECT {path}')
        await self.connect_target(path)
        await self.client_socket.sendall(RESPONSE.encode())
        data = b''

        while True:
            try:
                data = await self.client_socket.recv(BUFLEN)
                if data:
                    await self.target_socket.send(data)
                else:
                    break
            except Exception:
                break

    async def connect_target(self, host):
        i = host.find(':')
        if i != -1:
            port = int(host[i+1:])
            host = host[:i]
        else:
            if self.method == 'CONNECT':
                port = 443
            else:
                port = 80

        _, _, proto, _, address = socket.getaddrinfo(host, port)[0]

        self.target_socket = socket.socket(proto)
        self.target_socket.connect(address)

def main(host=LISTENING_ADDR, port=LISTENING_PORT):
    print("-------------- PythonProxy By Skynet --------------")
    print(f"-------------- LISTENING: {LISTENING_ADDR}:{LISTENING_PORT}")
    print("CONTACTO TELEGRAM @Skyn3tw0rks")
    print("Deje en Segundo Plano")
    print("Ctrl + a d")
    print(":---------------------------------------:")

    server = Server(host, port)
    server.start()

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        print('\033[31m' + 'Deteniendo' + '\033[0;0m')
        server.close()

if __name__ == '__main__':
    main()
    
