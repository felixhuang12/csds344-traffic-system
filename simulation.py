import random
import time
import threading
import pygame
import sys

signalCoords = [(480, 410), (530, 460), (480, 510), (430, 460)]
# signalCoords = [(150, 150), (200, 200), (150, 250), (100, 200)]
signals = []
directionNums: {0: 'up', 1: 'right', 2: 'down', 3: 'left'}
currGreenSignals = (0, 2) # 0 = up, 1 = right, 2 = down, 3 = left
nextGreenSignal = (1, 3)
yellowSignalFlag = True
speeds = {'car': 1.0, 'person': 0.5}

# Space between vehicles
gap = 25

carTurned = {'up': [], 'right': [], 'down': [], 'left': []}
carNotTurned = {'up': [], 'right': [], 'down': [], 'left': []}
rotationAngle = 3
greenSignalTime = 10
yellowSignalTime = 3
redSignalTime = 10

# starting vehicle coords
x = {'up': [420], 'right': [1000], 'down': [540], 'left': [0]}
y = {'up': [0], 'right': [420], 'down': [1000], 'left': [540]}


pygame.init()
simulation = pygame.sprite.Group()

class TrafficSignal:
    def __init__(self, redDuration: int, yellowDuration: int, greenDuration: int):
        self.redDuration = redDuration
        self.yellowDuration = yellowDuration
        self.greenDuration = greenDuration
        self.count = ''

class Car(pygame.sprite.Sprite):
    def __init__(self, startingDirNum: int):
        self.speed = speeds['car']
        self.startingDirection = directionNums[startingDirNum]
        validIndices = [i for i in range(len(directionNums)) if i != startingDirNum-1]
        self.destinationDirection = directionNums[validIndices[random.randint(0, 3)]]
        self.x = x[self.startingDirection]
        self.y = y[self.startingDirection]

def main():
    background = pygame.image.load('images/intersection.png')
    screenSize = (1000, 1000)
    screen = pygame.display.set_mode(size=screenSize)

    # Loading signal images and font
    redSignal = pygame.image.load('images/signals/red.png')
    yellowSignal = pygame.image.load('images/signals/yellow.png')
    greenSignal = pygame.image.load('images/signals/green.png')

    # example - TODO: delete
    car = pygame.image.load('images/car.png')
    car = pygame.transform.scale(car, (30, 30))
    car_x = 1000
    car_y = 420
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False
        
        screen.blit(background,(0,0))   # display background in simulation

        for i in range(0, 4):
            screen.blit(redSignal, signalCoords[i])
        car_x -= speeds['car']
        # car_y += speeds['car']
        screen.blit(car, (car_x, car_y))
        pygame.display.update()
        clock.tick(60)

main()
pygame.quit()
sys.exit()