import socket
import threading 
import logging
from urllib.parse import urlparse

# Configuración
LISTEN_ADDRESS = '0.0.0.0' 
LISTEN_PORT = 8080

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('proxy')

class ConnectionHandler(threading.Thread):
  """
  Clase para manejar cada conexión entrante
  """
  def __init__(self, client_socket, client_addr):
    threading.Thread.__init__(self)
    self.client = client_socket
    self.client_addr = client_addr
  
  def run(self):
    try:
      # Recibir datos
      data = self.client.recv(4096)  
      
      # Parsear URL
      url = urlparse(data)
      hostname = url.netloc
      
      # Conectar con el servidor
      server_socket = socket.socket()
      server_socket.connect((hostname, 80))
      
      # Enviar datos al servidor
      server_socket.send(data)  
      
      # Loop para reenviar datos entre el cliente y el servidor
      while True:
         client_data = self.client.recv(4096)
         server_socket.send(client_data)
         
         server_data = server_socket.recv(4096)
         self.client.send(server_data)
      
    except Exception as e:
      logger.error("Error: %s", e)
      self.client.close()
      server_socket.close()
      
    finally:
      logger.info("Conexión cerrada desde %s", self.client_addr)
      self.client.close()
      
class ProxyServer:
  "Servidor proxy escuchando en el puerto dado"
  
  def __init__(self, listen_addr, listen_port):
    self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.server.bind((listen_addr, listen_port))
  
  def start(self):
    self.server.listen(5) 
    while True:
      client_sock, client_addr = self.server.accept()
      logger.info("Nueva conexión desde %s", client_addr)
      client_thread = ConnectionHandler(client_sock, client_addr)
      client_thread.start()
      

if __name__ == '__main__':
    proxy = ProxyServer(LISTEN_ADDRESS, LISTEN_PORT)
    proxy.start()
