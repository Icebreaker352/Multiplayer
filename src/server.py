import socket, threading, time, os, json

os.system('clear')

Header = 8
port = 5000
host = '10.0.0.29'
addr = (host, port)
Disconnect = "!DISCONNECT!"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(addr)

players = {}
swords = {}
objects = []

class Msg:
    def __init__(self, data):
        self.data = data
    def send(self, conn):
        msg = json.dumps(self.data).encode('utf-8')
        msg_length = len(msg)
        send_length = str(msg_length).encode('utf-8') + b' ' * (Header - len(str(msg_length).encode('utf-8')))
        conn.send(send_length)
        conn.send(msg)
def handle_client(conn, addr):
    id = str(addr).split(', ')[1].replace(')', '')
    print(f'[CLIENTS] ({id}) has Connected')
    connected = True
    while connected:
        msg_length = conn.recv(Header).decode('utf-8')
        if msg_length:
            msg_length = int(msg_length)
            msg = json.loads(conn.recv(msg_length).decode('utf-8'))
            if msg['request'] == Disconnect:
                connected = False
                print(f'[CLIENTS] ({id}) has Disconnected')
                players.pop(id)
                break
            if msg['request'] == 'fetch':
                if msg['type'] == 'id':
                    Msg(id).send(conn)
                if msg['type'] == 'players':
                    players[id] = msg['data']
                    Msg(players).send(conn)
                if msg['type'] == 'objects':
                    Msg(objects).send(conn)
                if msg['type'] == 'swords':
                    swords[id] = msg['data']
                    Msg(swords).send(conn)
    conn.close()
def start():
    server.listen()
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

print('[SERVER] Server is starting...')
time.sleep(0.3)
print('[SERVER] Server is Up!')
start()