import random
import time
import threading
import pygame
import sys

### constants
directionNums = {0: 'up', 1: 'right', 2: 'down', 3: 'left'}
speeds = {'car': 2.0, 'person': 0.5}
signalCoords = [(480, 410), (530, 460), (480, 510), (430, 460)]
# signalCoords = [(150, 150), (200, 200), (150, 250), (100, 200)]
gap = 25
rotationAngle = 3
greenSignalTime = 10
yellowSignalTime = 3
redSignalTime = 10
# starting car coordinates
x = {'up': 420, 'right': 1000, 'down': 540, 'left': 30}
y = {'up': 30, 'right': 420, 'down': 1000, 'left': 540}
# x = {'down': [420], 'left': [1000], 'up': [540], 'right': [0]}
# y = {'down': [1000], 'left': [420], 'up': [0], 'right': [540]}
stopLines = {'up': 280, 'right': 700, 'down': 540, 'left': 280} # coming from up, right, down, left
turnThresholdLines = {'up': {'left': 410, 'right': 550},
                      'right': {'up': 550, 'down': 410}, 
                      'down': {'left': 410, 'right': 550},
                      'left': {'up': 550, 'down': 410}, 
                      } # coming from up, right, down, left


### global state
signals = []
currentGreenSignals = (0, 2) # 0 = up, 1 = right, 2 = down, 3 = left
nextGreenSignals = (1, 3)
yellowSignalFlag = False
carsTurned = {'up': [], 'right': [], 'down': [], 'left': []}
carsNotTurned = {'up': [], 'right': [], 'down': [], 'left': []}

### initialize pygame
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
        pygame.sprite.Sprite.__init__(self)
        self.speed = speeds['car']
        self.startingLocation = directionNums[startingDirNum]
        validIndices = [i for i in range(len(directionNums)) if i != startingDirNum]
        self.destinationDirection = directionNums[validIndices[random.randint(0, 2)]]
        self.x = x[self.startingLocation]
        self.y = y[self.startingLocation]
        self.originalImage = pygame.transform.scale(pygame.image.load('images/car.png'), (30, 30))
        self.image = pygame.transform.scale(pygame.image.load('images/car.png'), (30, 30))
        self.speed = speeds['car']
        simulation.add(self)
    
    def render(self, screen: pygame.surface.Surface):
        screen.blit(self.image, (self.x, self.y))
    
    def move(self):
        if (self.startingLocation == 'up'):
            if (self.destinationDirection == 'down'):
                if (currentGreenSignals == (0, 2) 
                    or ((yellowSignalFlag or currentGreenSignals != (0, 2)) and self.y < stopLines['up']) 
                    or self.y > stopLines['up']):
                    self.y += self.speed
                    
            elif (self.destinationDirection == 'left'):
                if (self.y == turnThresholdLines['up']['left']):
                    self.x -= self.speed
                elif ((currentGreenSignals == (0, 2) and self.y < turnThresholdLines['up']['left'])
                      or ((yellowSignalFlag or currentGreenSignals != (0, 2)) and self.y < stopLines['up'])
                      or (self.y > stopLines['up'] and self.y < turnThresholdLines['up']['left'])):
                    self.y += self.speed

            elif (self.destinationDirection == 'right'):
                if (self.y == turnThresholdLines['up']['right']):
                    self.x += self.speed
                elif ((currentGreenSignals == (0, 2) and self.y < turnThresholdLines['up']['right'])
                      or ((yellowSignalFlag or currentGreenSignals != (0, 2)) and self.y < stopLines['up'])
                      or (self.y > stopLines['up'] and self.y < turnThresholdLines['up']['right'])):
                    self.y += self.speed
                
        elif (self.startingLocation == 'down'):
            if (self.destinationDirection == 'up'):
                if (currentGreenSignals == (0, 2) 
                    or ((yellowSignalFlag or currentGreenSignals != (0, 2)) and self.y > stopLines['down']) 
                    or self.y < stopLines['down']):
                    self.y -= self.speed
                    
            elif (self.destinationDirection == 'left'):
                if (self.y == turnThresholdLines['down']['left']):
                    self.x -= self.speed
                elif ((currentGreenSignals == (0, 2) and self.y > turnThresholdLines['down']['left'])
                      or ((yellowSignalFlag or currentGreenSignals != (0, 2)) and self.y > stopLines['down'])
                      or (self.y < stopLines['down'] and self.y > turnThresholdLines['down']['left'])):
                    self.y -= self.speed

            elif (self.destinationDirection == 'right'):
                if (self.y == turnThresholdLines['down']['right']):
                    self.x += self.speed
                elif ((currentGreenSignals == (0, 2) and self.y > turnThresholdLines['down']['right'])
                      or ((yellowSignalFlag or currentGreenSignals != (0, 2)) and self.y > stopLines['down'])
                      or (self.y < stopLines['down'] and self.y > turnThresholdLines['down']['right'])):
                    self.y -= self.speed
                
        elif (self.startingLocation == 'left'):
            if (self.destinationDirection == 'right'):
                if (currentGreenSignals == (1, 3) 
                    or ((yellowSignalFlag or currentGreenSignals != (1, 3)) and self.x < stopLines['left']) 
                    or self.x > stopLines['left']):
                    self.x += self.speed
                    
            elif (self.destinationDirection == 'up'):
                if (self.x == turnThresholdLines['left']['up']):
                    self.y -= self.speed
                elif ((currentGreenSignals == (1, 3) and self.x < turnThresholdLines['left']['up'])
                      or ((yellowSignalFlag or currentGreenSignals != (1, 3)) and self.x < stopLines['left'])
                      or (self.x > stopLines['left'] and self.x < turnThresholdLines['left']['up'])):
                    self.x += self.speed

            elif (self.destinationDirection == 'down'):
                if (self.x == turnThresholdLines['left']['down']):
                    self.y += self.speed
                elif ((currentGreenSignals == (1, 3) and self.x < turnThresholdLines['left']['down'])
                      or ((yellowSignalFlag or currentGreenSignals != (1, 3)) and self.x < stopLines['left'])
                      or (self.x > stopLines['left'] and self.x < turnThresholdLines['left']['down'])):
                    self.x += self.speed

        elif (self.startingLocation == 'right'):
            if (self.destinationDirection == 'left'):
                if (currentGreenSignals == (1, 3) 
                    or ((yellowSignalFlag or currentGreenSignals != (1, 3)) and self.x > stopLines['right']) 
                    or self.x < stopLines['right']):
                    self.x -= self.speed
                    
            elif (self.destinationDirection == 'up'):
                if (self.x == turnThresholdLines['right']['up']):
                    self.y -= self.speed
                elif ((currentGreenSignals == (1, 3) and self.x > turnThresholdLines['right']['up'])
                      or ((yellowSignalFlag or currentGreenSignals != (1, 3)) and self.x > stopLines['right'])
                      or (self.x < stopLines['right'] and self.x > turnThresholdLines['right']['up'])):
                    self.x -= self.speed

            elif (self.destinationDirection == 'down'):
                if (self.x == turnThresholdLines['right']['down']):
                    self.y += self.speed
                elif ((currentGreenSignals == (1, 3) and self.x > turnThresholdLines['right']['down'])
                      or ((yellowSignalFlag or currentGreenSignals != (1, 3)) and self.x > stopLines['right'])
                      or (self.x < stopLines['right'] and self.x > turnThresholdLines['right']['down'])):
                    self.x -= self.speed

def main():
    background = pygame.image.load('images/intersection.png')
    screenSize = (1000, 1000)
    screen = pygame.display.set_mode(size=screenSize)

    # Loading signal images and font
    redSignal = pygame.image.load('images/signals/red.png')
    yellowSignal = pygame.image.load('images/signals/yellow.png')
    greenSignal = pygame.image.load('images/signals/green.png')

    # example - TODO: delete
    # car = pygame.image.load('images/car.png')
    # car = pygame.transform.scale(car, (30, 30))
    # car_x = 1000
    # car_y = 420
    running = True
    clock = pygame.time.Clock()

    car = Car(3)

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
        # if (car_x >= 560):
        #     car_x -= speeds['car']
            # car_y += speeds['car']
        # screen.blit(car, (car_x, car_y))
        for car in simulation:
            car.render(screen)
            car.move()
        pygame.display.update()
        clock.tick(60)

main()
pygame.quit()
sys.exit()