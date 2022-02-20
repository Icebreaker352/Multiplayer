import pygame

pygame.init()
font = pygame.font.Font(None, 18)

def debug(data, y=10, x=10):
    screen = pygame.display.get_surface()
    txt = font.render(str(data), True, 'white')
    rect = txt.get_rect(topleft=(x, y))
    pygame.draw.rect(screen, 'black', rect)
    screen.blit(txt, rect)