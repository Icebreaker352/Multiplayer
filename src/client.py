import pygame, os, math, socket, json, sys, random
from debug import debug
from res.assets.assets import get

# Clear Console
os.system('clear')

# Constants
Header = 8
port = 8000
host = '10.0.0.29'
addr = (host, port)
Disconnect = "!DISCONNECT!"

# Connect to Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(addr)

# Create Server messaging Class
class Msg:
    def __init__(self, request, type='null', data='null'):
        self.request = request
        self.type = type
        self.data = data
    def send(self):
        msg = json.dumps({"request": self.request, "type": self.type, "data": json.dumps(self.data)}).encode('utf-8')
        msg_length = len(msg)
        send_length = str(msg_length).encode('utf-8') + b' ' * (Header - len(str(msg_length).encode('utf-8')))
        client.send(send_length)
        client.send(msg)
        msg_length = client.recv(Header).decode('utf-8')
        if msg_length:
            msg_length = int(msg_length)
            recv = json.loads(client.recv(msg_length).decode('utf-8'))
            return recv

# Get ID
id = Msg('fetch', 'id').send()

# Setup Client-Side Stuff
pygame.init()
pygame.display.set_icon(get('icon'))
pygame.display.set_caption('Client')
screen = pygame.display.set_mode((400, 400))
clock = pygame.time.Clock()

class Controller:
    def __init__(self):
        self.keys = {"up": False, "down": False, "left": False, "right": False}
    def check(self):
        self.keys["right"] = pygame.key.get_pressed()[pygame.K_RIGHT]|pygame.key.get_pressed()[pygame.K_d]
        self.keys["left"] = pygame.key.get_pressed()[pygame.K_LEFT]|pygame.key.get_pressed()[pygame.K_a]
        self.keys["up"] = pygame.key.get_pressed()[pygame.K_UP]|pygame.key.get_pressed()[pygame.K_w]
        self.keys["down"] = pygame.key.get_pressed()[pygame.K_DOWN]|pygame.key.get_pressed()[pygame.K_s]
        return self.keys
class Player:
    def __init__(self, rect, speed=5):
        self.rect = rect
        self.atr = {'health': 3, 'atkCool': 0}
        self.xv = 0
        self.yv = 0
        self.speed = speed
    def tick(self, daggers):
        keys = Controller().check()
        # Movement
        self.xv = 0
        self.yv = 0
        if keys["right"]: self.xv = self.speed
        if keys["left"]: self.xv = -self.speed
        if keys["up"]: self.yv = -self.speed
        if keys['down']: self.yv = self.speed
        self.rect.x += int(self.xv)
        self.rect.y += int(self.yv)
        # Check Collision with Dagger
        for dagger in daggers:
            dagr = daggers[dagger]
            dagrRect = pygame.Rect(dagr['pos'][0], dagr['pos'][1], 32, 32)
            if self.rect.colliderect(dagrRect):
                if not dagger == id:
                    Msg('remove', 'dagger', dagger).send()
                    self.atr['health'] -= 1
        self.atr['atkCool'] -= 1

        if self.atr['health'] < 1:
            Msg(Disconnect).send()
            sys.exit()
    def attack(self, pos):
        if self.atr['atkCool'] > 0: return
        dagger = {'pos': [0, 0], 'angle': (360-math.atan2(pos[1]-self.rect.y + self.rect.height/2, pos[0]-self.rect.x + self.rect.width/2)*180/math.pi)+random.randrange(-10, 10), 'cooldown': 45}
        Msg('add', 'dagger', dagger).send()
        self.atr['atkCool'] = 45

player = Player(pygame.Rect(20, 20, 25, 25), 5)

# Game Loop
running = True
while running:
    # Handle Events
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            player.attack(pygame.mouse.get_pos())
        # Quit Pygame
        if event.type == pygame.QUIT:
            running = False
    # Exchange Data
    rect = [player.rect.x, player.rect.y, player.rect.width, player.rect.height]
    players = Msg('fetch', 'players', {'rect': rect, 'atr': player.atr}).send()
    daggers = Msg('fetch', 'daggers').send()
    # Tick
    player.tick(daggers)
    # Render
    screen.fill((230, 50, 50))
    for key in players:
        color = (70, 70, 70)
        if key == id:
            color = (255, 255, 255)
        rect = json.loads(players[key])['rect']
        pygame.draw.rect(screen, color, pygame.Rect(rect[0], rect[1], rect[2], rect[3]))
    for dagger in daggers:
        dagr = daggers[dagger]
        if dagr['cooldown'] > 0:
            img = pygame.transform.rotate(get('dagger', 4), dagr['angle'] - 45)
            rect = img.get_rect(center=(dagr['pos'][0], dagr['pos'][1]))
            screen.blit(img, rect)
    debug(player.atr['health'])
    pygame.display.update()
    # Set FPS
    clock.tick(60)

Msg(Disconnect).send()