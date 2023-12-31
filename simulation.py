import random
import time
import threading
import pygame
import sys

### constants
speeds = {'car': 2.0, 'person': 2.0}
## pedestrians
pedestrianDirections = {
    'nw': {
        0: 'right',
        1: 'down'
    },
    'ne': {
        0: 'left',
        1: 'down'
    },
    'se': {
        0: 'left',
        1: 'up'
    },
    'sw': {
        0: 'right',
        1: 'up'
    }
}

pedestrianStartingPositions = {0: 'nw', 1: 'ne', 2: 'se', 3: 'sw'}

pedestrianStartingCoords = {
    'nw': (320, 340),
    'ne': (640, 320),
    'se': (660, 620),
    'sw': (340, 640)
}

## cars
directionNums = {0: 'up', 1: 'right', 2: 'down', 3: 'left'}
# starting car coordinates
x = {'up': 420, 'right': 1000, 'down': 540, 'left': 0}
y = {'up': 0, 'right': 420, 'down': 1000, 'left': 540}
stopLines = {'up': 280, 'right': 700, 'down': 690, 'left': 280} # coming from up, right, down, left
turnThresholdLines = {  # coming from up, right, down, left
    'up': {'left': 410, 'right': 550},
    'right': {'up': 550, 'down': 410}, 
    'down': {'left': 410, 'right': 550},
    'left': {'up': 550, 'down': 410}, 
}

## signals
signalCoords = [(480, 410), (530, 460), (480, 510), (430, 460)]
signalTextCoords = [(480, 390), (560, 460), (480, 560), (410, 460)]
defaultGreenSignalDuration = 10
defaultYellowSignalDuration = 3
defaultRedSignalDuration = 13

### global state
signals = []
currentGreenSignals = 0 # 0 north/south; 1 = west/east
nextGreenSignals = 1 # 0 north/south; 1 = west/east
yellowSignalFlag = False
carsTurned = {'up': [], 'right': [], 'down': [], 'left': []}
carsNotTurned = {'up': [], 'right': [], 'down': [], 'left': []}

### initialize pygame
pygame.init()
simulatedCars = pygame.sprite.Group()
simulatedPedestrians = pygame.sprite.Group()

pedestriansInNorthCrossWalk = set()
pedestriansInEastCrossWalk = set()
pedestriansInSouthCrossWalk = set()
pedestriansInWestCrossWalk = set()

def northCrossWalkEmpty():
    return len(pedestriansInNorthCrossWalk) == 0
def eastCrossWalkEmpty():
    return len(pedestriansInEastCrossWalk) == 0
def southCrossWalkEmpty():
    return len(pedestriansInSouthCrossWalk) == 0
def westCrossWalkEmpty():
    return len(pedestriansInWestCrossWalk) == 0

class Pedestrian(pygame.sprite.Sprite):
    def __init__(self, startingPositionNum: int, id: int):
        pygame.sprite.Sprite.__init__(self)
        self.startingPosition = pedestrianStartingPositions[startingPositionNum]
        self.movingDirection = pedestrianDirections[self.startingPosition][random.randint(0, 1)]
        self.coords = pedestrianStartingCoords[self.startingPosition]
        self.x = self.coords[0]
        self.y = self.coords[1]
        self.image = pygame.transform.scale(pygame.image.load('images/person.png'), (20, 20))
        self.speed = speeds['person']
        self.id = id
        simulatedPedestrians.add(self)
    
    def render(self, screen: pygame.surface.Surface):
        screen.blit(self.image, (self.x, self.y))

    def move(self):
        if (self.startingPosition == 'nw'):
            if ((self.movingDirection == 'right' and currentGreenSignals == 1) or self.x > pedestrianStartingCoords['nw'][0]):
                self.x += self.speed
                pedestriansInNorthCrossWalk.add(self.id)
                if (self.x > pedestrianStartingCoords['ne'][0]):
                    simulatedPedestrians.remove(self)
                    pedestriansInNorthCrossWalk.remove(self.id)
            elif ((self.movingDirection == 'down' and currentGreenSignals == 0) or self.y > pedestrianStartingCoords['nw'][1]):
                self.y += self.speed
                pedestriansInWestCrossWalk.add(self.id)
                if (self.y > pedestrianStartingCoords['sw'][1]):
                    simulatedPedestrians.remove(self)
                    pedestriansInWestCrossWalk.remove(self.id)
        elif (self.startingPosition == 'ne'):
            if ((self.movingDirection == 'left' and currentGreenSignals == 1) or self.x < pedestrianStartingCoords['ne'][0]):
                self.x -= self.speed
                pedestriansInNorthCrossWalk.add(self.id)
                if (self.x < pedestrianStartingCoords['nw'][0]):
                    simulatedPedestrians.remove(self)
                    pedestriansInNorthCrossWalk.remove(self.id)
            elif ((self.movingDirection == 'down' and currentGreenSignals == 0) or self.y > pedestrianStartingCoords['ne'][1]):
                self.y += self.speed
                pedestriansInEastCrossWalk.add(self.id)
                if (self.y > pedestrianStartingCoords['se'][1]):
                    simulatedPedestrians.remove(self)
                    pedestriansInEastCrossWalk.remove(self.id)
        elif (self.startingPosition == 'se'):
            if ((self.movingDirection == 'left' and currentGreenSignals == 1) or self.x < pedestrianStartingCoords['se'][0]):
                self.x -= self.speed
                pedestriansInSouthCrossWalk.add(self.id)
                if (self.x < pedestrianStartingCoords['sw'][0]):
                    simulatedPedestrians.remove(self)
                    pedestriansInSouthCrossWalk.remove(self.id)
            elif ((self.movingDirection == 'up' and currentGreenSignals == 0) or self.y < pedestrianStartingCoords['se'][1]):
                self.y -= self.speed
                pedestriansInEastCrossWalk.add(self.id)
                if (self.y < pedestrianStartingCoords['ne'][1]):
                    simulatedPedestrians.remove(self)
                    pedestriansInEastCrossWalk.remove(self.id)
        elif (self.startingPosition == 'sw'):
            if ((self.movingDirection == 'right' and currentGreenSignals == 1) or self.x > pedestrianStartingCoords['sw'][0]):
                self.x += self.speed
                pedestriansInSouthCrossWalk.add(self.id)
                if (self.x > pedestrianStartingCoords['se'][0]):
                    simulatedPedestrians.remove(self)
                    pedestriansInSouthCrossWalk.remove(self.id)
            elif ((self.movingDirection == 'up' and currentGreenSignals == 0) or self.y < pedestrianStartingCoords['sw'][1]):
                self.y -= self.speed
                pedestriansInWestCrossWalk.add(self.id)
                if (self.y < pedestrianStartingCoords['nw'][1]):
                    simulatedPedestrians.remove(self)
                    pedestriansInWestCrossWalk.remove(self.id)

def generatePedestrians():
    count = 1
    while (True):
        Pedestrian(random.randint(0, 3), count)
        count += 1
        time.sleep(5)

class TrafficSignal:
    def __init__(self, redDuration: int, yellowDuration: int, greenDuration: int):
        self.redDuration = redDuration
        self.yellowDuration = yellowDuration
        self.greenDuration = greenDuration
        self.text = ''

class Car(pygame.sprite.Sprite):
    def __init__(self, startingDirNum: int):
        pygame.sprite.Sprite.__init__(self)
        self.speed = speeds['car']
        self.startingLocation = directionNums[startingDirNum]
        validIndices = [i for i in range(len(directionNums)) if i != startingDirNum]
        self.destinationDirection = directionNums[validIndices[random.randint(0, 2)]]
        self.x = x[self.startingLocation]
        self.y = y[self.startingLocation]
        self.image = pygame.transform.scale(pygame.image.load('images/car.png'), (30, 30))
        self.speed = speeds['car']
        simulatedCars.add(self)
    
    def render(self, screen: pygame.surface.Surface):
        screen.blit(self.image, (self.x, self.y))
    
    def move(self):
        if (self.startingLocation == 'up'):
            if (self.destinationDirection == 'down'):
                if (currentGreenSignals == 0 
                    or ((yellowSignalFlag or currentGreenSignals != 0) and self.y < stopLines['up']) 
                    or self.y > stopLines['up']):
                    if ((self.y == stopLines['up'] and not northCrossWalkEmpty()) or (self.y < stopLines['down'] - 100 and not southCrossWalkEmpty())):
                        pass
                    else:
                        self.y += self.speed

            elif (self.destinationDirection == 'left'):
                if (self.x < stopLines['left'] + 100 and self.y == turnThresholdLines['up']['left']):
                    self.x -= self.speed
                elif (self.y == turnThresholdLines['up']['left']):
                    if (self.x > stopLines['left'] + 100 or (self.x == stopLines['left'] + 100 and westCrossWalkEmpty())):
                        self.x -= self.speed
                elif ((currentGreenSignals == 0 and self.y < turnThresholdLines['up']['left'])
                      or ((yellowSignalFlag or currentGreenSignals != 0) and self.y < stopLines['up'])
                      or (self.y > stopLines['up'] and self.y < turnThresholdLines['up']['left'])):
                    if (self.y == stopLines['up'] and not northCrossWalkEmpty()):
                        pass
                    else:
                        self.y += self.speed

            elif (self.destinationDirection == 'right'):
                if (self.x > stopLines['right'] - 100 and self.y == turnThresholdLines['up']['right']):
                    self.x += self.speed
                elif (self.y == turnThresholdLines['up']['right']):
                    if (self.x < stopLines['right'] - 100 or (self.x == stopLines['right'] - 100 and eastCrossWalkEmpty())):
                        self.x += self.speed
                elif ((currentGreenSignals == 0 and self.y < turnThresholdLines['up']['right'])
                      or ((yellowSignalFlag or currentGreenSignals != 0) and self.y < stopLines['up'])
                      or (self.y > stopLines['up'] and self.y < turnThresholdLines['up']['right'])):
                    if (self.y == stopLines['up'] and not northCrossWalkEmpty()):
                        pass
                    else:
                        self.y += self.speed
                
        elif (self.startingLocation == 'down'):
            if (self.destinationDirection == 'up'):
                if (currentGreenSignals == 0 
                    or ((yellowSignalFlag or currentGreenSignals != 0) and self.y > stopLines['down']) 
                    or self.y < stopLines['down']):
                    if ((self.y == stopLines['down'] and not southCrossWalkEmpty()) or (self.y > stopLines['up'] + 100 and not northCrossWalkEmpty())):
                        pass
                    else:
                        self.y -= self.speed
                    
            elif (self.destinationDirection == 'left'):
                if (self.x < stopLines['left'] + 100 and self.y == turnThresholdLines['up']['left']):
                    self.x -= self.speed
                elif (self.y == turnThresholdLines['up']['left']):
                    if (self.x > stopLines['left'] + 100 or (self.x == stopLines['left'] + 100 and westCrossWalkEmpty())):
                        self.x -= self.speed
                elif ((currentGreenSignals == 0 and self.y > turnThresholdLines['down']['left'])
                      or ((yellowSignalFlag or currentGreenSignals != 0) and self.y > stopLines['down'])
                      or (self.y < stopLines['down'] and self.y > turnThresholdLines['down']['left'])):
                    if (self.y == stopLines['down'] and not southCrossWalkEmpty()):
                        pass
                    else:
                        self.y -= self.speed

            elif (self.destinationDirection == 'right'):
                if (self.x > stopLines['right'] - 100 and self.y == turnThresholdLines['up']['right']):
                    self.x += self.speed
                elif (self.y == turnThresholdLines['up']['right']):
                    if (self.x < stopLines['right'] - 100 or (self.x == stopLines['right'] - 100 and eastCrossWalkEmpty())):
                        self.x += self.speed
                elif ((currentGreenSignals == 0 and self.y > turnThresholdLines['down']['right'])
                      or ((yellowSignalFlag or currentGreenSignals != 0) and self.y > stopLines['down'])
                      or (self.y < stopLines['down'] and self.y > turnThresholdLines['down']['right'])):
                    if (self.y == stopLines['down'] and not southCrossWalkEmpty()):
                        pass
                    else:
                        self.y -= self.speed
                
        elif (self.startingLocation == 'left'):
            if (self.destinationDirection == 'right'):
                if (currentGreenSignals == 1 
                    or ((yellowSignalFlag or currentGreenSignals != 1) and self.x < stopLines['left']) 
                    or self.x > stopLines['left']):
                    if ((self.x == stopLines['left'] and not westCrossWalkEmpty()) or (self.x < stopLines['right'] - 100 and not eastCrossWalkEmpty())):
                        pass
                    else:
                        self.x += self.speed
                    
            elif (self.destinationDirection == 'up'):
                if (self.y < stopLines['up'] + 100 and self.x == turnThresholdLines['left']['up']):
                    self.y -= self.speed
                elif (self.x == turnThresholdLines['left']['up']):
                    if (self.y > stopLines['up'] + 100 or (self.y == stopLines['up'] + 100 and northCrossWalkEmpty())):
                        self.y -= self.speed
                elif ((currentGreenSignals == 1 and self.x < turnThresholdLines['left']['up'])
                      or ((yellowSignalFlag or currentGreenSignals != 1) and self.x < stopLines['left'])
                      or (self.x > stopLines['left'] and self.x < turnThresholdLines['left']['up'])):
                    if (self.x == stopLines['left'] and not westCrossWalkEmpty()):
                        pass
                    else:
                        self.x += self.speed

            elif (self.destinationDirection == 'down'):
                if (self.y > stopLines['down'] - 100 and self.x == turnThresholdLines['left']['down']):
                    self.y += self.speed
                elif (self.x == turnThresholdLines['left']['down']):
                    if (self.y < stopLines['down'] - 100 or (self.y == stopLines['down'] - 100 and southCrossWalkEmpty())):
                        self.y += self.speed
                elif ((currentGreenSignals == 1 and self.x < turnThresholdLines['left']['down'])
                      or ((yellowSignalFlag or currentGreenSignals != 1) and self.x < stopLines['left'])
                      or (self.x > stopLines['left'] and self.x < turnThresholdLines['left']['down'])):
                    if (self.x == stopLines['left'] and not westCrossWalkEmpty()):
                        pass
                    else:
                        self.x += self.speed

        elif (self.startingLocation == 'right'):
            if (self.destinationDirection == 'left'):
                if (currentGreenSignals == 1 
                    or ((yellowSignalFlag or currentGreenSignals != 1) and self.x > stopLines['right']) 
                    or self.x < stopLines['right']):
                    if ((self.x == stopLines['right'] and not eastCrossWalkEmpty()) or (self.x > stopLines['left'] + 100 and not westCrossWalkEmpty())):
                        pass
                    else:
                        self.x -= self.speed
                    
            elif (self.destinationDirection == 'up'):
                if (self.y < stopLines['up'] + 100 and self.x == turnThresholdLines['left']['up']):
                    self.y -= self.speed
                elif (self.x == turnThresholdLines['left']['up']):
                    if (self.y > stopLines['up'] + 100 or (self.y == stopLines['up'] + 100 and northCrossWalkEmpty())):
                        self.y -= self.speed
                elif ((currentGreenSignals == 1 and self.x > turnThresholdLines['right']['up'])
                      or ((yellowSignalFlag or currentGreenSignals != 1) and self.x > stopLines['right'])
                      or (self.x < stopLines['right'] and self.x > turnThresholdLines['right']['up'])):
                    if (self.x == stopLines['right'] and not eastCrossWalkEmpty()):
                        pass
                    else:
                        self.x -= self.speed

            elif (self.destinationDirection == 'down'):
                if (self.y > stopLines['down'] - 100 and self.x == turnThresholdLines['left']['down']):
                    self.y += self.speed
                elif (self.x == turnThresholdLines['left']['down']):
                    if (self.y < stopLines['down'] - 100 or (self.y == stopLines['down'] - 100 and southCrossWalkEmpty())):
                        self.y += self.speed
                elif ((currentGreenSignals == 1 and self.x > turnThresholdLines['right']['down'])
                      or ((yellowSignalFlag or currentGreenSignals != 1) and self.x > stopLines['right'])
                      or (self.x < stopLines['right'] and self.x > turnThresholdLines['right']['down'])):
                    if (self.x == stopLines['right'] and not eastCrossWalkEmpty()):
                        pass
                    else:
                        self.x -= self.speed

def generateCars():
    while (True):
        Car(random.randint(0, 3))
        time.sleep(5)

def initializeSignals():
    signal = TrafficSignal(defaultRedSignalDuration, defaultYellowSignalDuration, defaultGreenSignalDuration)
    global signals
    signals = [signal, signal, signal, signal]
    simulate()

def simulate():
    global currentGreenSignals, yellowSignalFlag, nextGreenSignals

    while (signals[currentGreenSignals].greenDuration > 0):
        updateSignals()
        time.sleep(1)

    yellowSignalFlag = True

    while(signals[currentGreenSignals].yellowDuration > 0):
        updateSignals()
        time.sleep(1)
    
    yellowSignalFlag = False
    signals[currentGreenSignals].greenDuration = defaultGreenSignalDuration
    signals[currentGreenSignals].yellowDuration = defaultYellowSignalDuration
    signals[currentGreenSignals].redDuration = defaultRedSignalDuration
    temp = currentGreenSignals
    currentGreenSignals = nextGreenSignals
    nextGreenSignals = temp
    simulate()

def updateSignals():
    for i in range(0, 2):
        if (i == currentGreenSignals):
            if (not yellowSignalFlag):
                signals[i].greenDuration -= 1
            else:
                signals[i].yellowDuration -= 1
        else:
            signals[i].redDuration -= 1


def main():
    background = pygame.image.load('images/intersection.png')
    screenSize = (1000, 1000)
    screen = pygame.display.set_mode(size=screenSize)

    # Loading signal images and font
    redSignal = pygame.image.load('images/signals/red.png')
    yellowSignal = pygame.image.load('images/signals/yellow.png')
    greenSignal = pygame.image.load('images/signals/green.png')


    signalThread = threading.Thread(name="init", target=initializeSignals, args=())
    signalThread.daemon = True
    signalThread.start()
    
    # generate cars
    carThread = threading.Thread(name="generateCars", target=generateCars, args=())
    carThread.daemon = True
    carThread.start()

    # generate pedestrians
    pedestrianThread = threading.Thread(name="generatePedestrians", target=generatePedestrians, args=())
    pedestrianThread.daemon = True
    pedestrianThread.start()
    
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

        font = pygame.font.Font(None, 30)
        screen.blit(background,(0,0))   # display background in simulation
        
        for i in range(0, 2):
            # display signal
            if (i == currentGreenSignals):
                if (yellowSignalFlag):
                    signals[i].text = signals[i].yellowDuration
                    signals[i+2].text = signals[i+2].yellowDuration
                    screen.blit(yellowSignal, signalCoords[i])
                    screen.blit(yellowSignal, signalCoords[i+2])
                else:
                    signals[i].text = signals[i].greenDuration
                    signals[i+2].text = signals[i+2].greenDuration
                    screen.blit(greenSignal, signalCoords[i])
                    screen.blit(greenSignal, signalCoords[i+2])
            else:
                signals[i].text = signals[i].redDuration
                signals[i+2].text = signals[i+2].redDuration
                screen.blit(redSignal, signalCoords[i])
                screen.blit(redSignal, signalCoords[i+2])
            
            # display timer
            signalText = font.render(str(signals[i].text), True, (255, 255, 255), (0, 0, 0))
            screen.blit(signalText, signalTextCoords[i])
            screen.blit(signalText, signalTextCoords[i+2])

        # display cars
        for car in simulatedCars:
            car.render(screen)
            car.move()
        
        # display pedestrians
        for pedestrian in simulatedPedestrians:
            pedestrian.render(screen)
            pedestrian.move()

        pygame.display.update()
        clock.tick(60)

main()
pygame.quit()
sys.exit()