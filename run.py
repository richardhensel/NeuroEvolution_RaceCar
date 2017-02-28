import os, sys, math, pygame, pygame.mixer
import random
import euclid
from pygame.locals import *

from Car import Car


# inputs: four tuples each representing a line segment point

#Line1: p1,p2
#Line2: p3,p4

def get_line_intersection(p1, p2, p3, p4):
    s1 = (p2[0] - p1[0], p2[1] - p1[1])
    s2 = (p4[0] - p3[0], p4[1] - p3[1])

    s = (-s1[1] * (p1[0] - p3[0]) + s1[0] * (p1[1] - p3[1])) / (-s2[0] * s1[1] + s1[0] * s2[1]);
    t = ( s2[0] * (p1[1] - p3[1]) - s2[1] * (p1[0] - p3[0])) / (-s2[0] * s1[1] + s1[0] * s2[1]);

    if (s >= 0 and s <= 1 and t >= 0 and t <= 1):
        
        i_x = p1[0] + (t * s1[0])
        i_y = p1[1] + (t * s1[1])
        return i_x, i_y # Collision detected

    else:
        return 0 # No collision



black = 0,0,0
white = 255,255,255
red = 255, 0, 0
green = 0, 255, 0
blue = 0, 0, 255

screenSize = screenWidth, screenHeight = 1000, 700

# Set the screen size
screen = pygame.display.set_mode(screenSize)

clock = pygame.time.Clock()
fpsLimit = 60
runMe = True

car = Car(euclid.Vector3(300., 200., 0.), euclid.Vector3(1.,0., 0.))

obstacle1 = [(400,100), (400, 300), (500, 200)]
obstacle2 = [(500,500), (900, 500), (400, 700)]

car.control(30.0, 0.0001)

while runMe:

    #get user input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            runMe = False

    #Limit the framerate
    dtime_ms = clock.tick(fpsLimit)
    dtime = dtime_ms/1000.0

    screen.fill(white)

    #draw obstacles
    pygame.draw.lines(screen, (0,0,0), True, obstacle1, 5)
    pygame.draw.lines(screen, (0,0,0), True, obstacle2, 5)

    car.move(dtime)
    car.sense(obstacle1)
    car.sense(obstacle2)
    car.detect_collision(obstacle1)
    car.detect_collision(obstacle2)
    car.display(screen)
    car.reset_sensors()

    screen.unlock()

    pygame.display.flip()

pygame.quit()
sys.exit()
