import socket
import threading
import time
import logging
from copy import deepcopy
from datetime import datetime
from constants import BROADCAST_ADDRESS, BROADCAST_PORT, BUFFERSIZE, TIMEOUT

# loggig change to level = logging.DEBUG to see all the debug logs
logging.basicConfig(level=logging.INFO)

class Peer():
    def __init__(self, nickname = "Anonymous"):

        # socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind(('', BROADCAST_PORT))

        self.sock.settimeout(TIMEOUT)

        self.own_address = socket.gethostbyname(socket.gethostname())

        # (address, port) : last_active time
        self.clients = {}

        self.nickname = nickname

        # ping thread
        self.ping_thread = threading.Thread(target=self._broadcast_ping)

        # listen thread
        self.listen_tread = threading.Thread(target=self._listen_for_messages)

        self.stopped = False

    def change_nickname(self, nickname):
        self.nickname = nickname


    def get_clients(self):
        return self.clients

    def start_threads(self):
        self.stopped = False
        self.ping_thread.start()
        self.listen_tread.start()
        logging.debug('Threads started')

    def stop_threads(self):
        self.stopped = True
        self.ping_thread.join()
        self.listen_tread.join()
        logging.debug('Threads joined')

    def close(self):
        self.sock.close()
        logging.debug('Socket closed')

    def send_message(self, message):

        # add time and nickname to massage
        msg_curr_time = datetime.now().strftime("%H:%M:%S")
        message_to_send = f'[{msg_curr_time}]({self.own_address}) {self.nickname}: {message}'

        # send to all clients seperatly (except self)
        for client_address in self.clients:
            if client_address[0] != self.own_address: 
                self.sock.sendto(message_to_send.encode('utf-8'), client_address)

        # print so the user sees what he sent
        print(f'[{msg_curr_time}]({self.own_address}) {self.nickname}(You): {message}')

        logging.debug("message sent")

    def _broadcast_ping(self):
        while not self.stopped:

            # Remove inactive clients
            for c_address in deepcopy(self.clients):
                if time.time() - self.clients[c_address] > 0.4:
                    self.clients.pop(c_address)
                    if c_address != self.own_address:
                        print(f"Client {c_address[0]} left the chat")
                    logging.debug(f"Client {c_address} removed")
            
            # Send a PING message to the broadcast address
            self.sock.sendto(b'PING', (BROADCAST_ADDRESS, BROADCAST_PORT))
            time.sleep(0.1)

    def _listen_for_messages(self):
        while not self.stopped:
            try:
                data, address = self.sock.recvfrom(BUFFERSIZE)
                self._handle_message(data, address)
            except socket.timeout:
                pass

    def _handle_message(self, data, address):

        # If the message is a ping, add to list or update old time, else print the message
        if data == b'PING':
            logging.debug(f"PING recieved from {address}")
            if address not in self.clients:
                if address[0] != self.own_address:
                    print(f"Client {address[0]} joined the chat")
                logging.debug(f"Client {address} added")
            self.clients[address] = time.time()
        else:
            message = data.decode('utf-8')
            logging.debug(f"message recieved from {address}: {message}")
            print(message)