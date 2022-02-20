import pygame, os, math, socket, json, assets.assets as assets
from debug import debug

os.system('clear')

Header = 8
port = 5000
host = '10.0.0.29'
addr = (host, port)
Disconnect = "!DISCONNECT!"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(addr)

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

id = Msg('fetch', 'id').send()
pygame.init()
screen = pygame.display.set_mode((400, 400))
clock = pygame.time.Clock()
pygame.display.set_icon(assets.get('icon'))

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
        self.dagr = {'cooldown': 0, 'angle': 0, 'pos': [0, 0]}
        self.atr = {}
        self.xv = 0
        self.yv = 0
        self.speed = speed
    def tick(self, objects):
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
        # Object Collision®
        for obj in objects:
            rect = self.rect
            obj = pygame.Rect(obj[0], obj[1], obj[2], obj[3])
            if rect.colliderect(obj):
                if abs(obj.top - rect.bottom) < 10: self.rect.y -= round(self.yv)
                if abs(obj.bottom - rect.top) < 10: self.rect.y -= round(self.yv)
                if abs(obj.right - rect.left) < 10: self.rect.x -= round(self.xv)
                if abs(obj.left - rect.right) < 10: self.rect.x -= round(self.xv)
        # Change Attack Cooldown
        self.dagr['cooldown'] -= 1
        if self.dagr['cooldown'] > 0 and self.dagr['cooldown'] < 30:
            vec = pygame.math.Vector2()
            vec.from_polar((5, self.dagr['angle']*-1))
            self.dagr['pos'][0] += vec[0]
            self.dagr['pos'][1] += vec[1]
    def attack(self, pos):
        if dagr['cooldown'] > 0:
            return
        self.dagr['pos'] = [self.rect.x + self.rect.width/2, self.rect.y + self.rect.height/2]
        self.dagr['angle'] = 360-math.atan2(pos[1]-self.dagr['pos'][1], pos[0]-self.dagr['pos'][0])*180/math.pi
        self.dagr['cooldown'] = 45
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
    objects = Msg('fetch', 'objects').send()
    daggers = Msg('fetch', 'daggers', player.dagr).send()
    # Tick
    player.tick(objects)
    # Render
    screen.fill((230, 50, 50))
    for obj in objects:
        pygame.draw.rect(screen, (0, 255, 255), pygame.Rect(obj[0], obj[1], obj[2], obj[3]))
    for key in players:
        color = (70, 70, 70)
        if key == id:
            color = (255, 255, 255)
        rect = json.loads(players[key])['rect']
        pygame.draw.rect(screen, color, pygame.Rect(rect[0], rect[1], rect[2], rect[3]))
    for dagger in daggers:
        dagr = json.loads(daggers[dagger])
        if dagr['cooldown'] > 0:
            img = pygame.transform.rotate(assets.get('dagger', 4), dagr['angle'] - 45)
            rect = img.get_rect(center=(dagr['pos'][0], dagr['pos'][1]))
            screen.blit(img, rect)
    debug(id)
    pygame.display.update()
    # Set FPS
    clock.tick(60)

Msg(Disconnect).send()
