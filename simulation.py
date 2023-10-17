import pygame
import sys

pygame.init()
simulation = pygame.sprite.Group()

def main():
    background = pygame.image.load('images/intersection.png')
    screenSize = (1000, 1000)
    screen = pygame.display.set_mode(size=screenSize)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        
        screen.blit(background,(0,0))   # display background in simulation
        pygame.display.update()

main()