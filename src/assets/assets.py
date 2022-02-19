import pygame, os

pygame.init()

def get(path, scale=1):
    path = __file__.replace('assets.py', 'textures/') + path + '.png'
    img = pygame.image.load(path)
    return pygame.transform.scale(img, (img.get_width() * scale, img.get_width() * scale))