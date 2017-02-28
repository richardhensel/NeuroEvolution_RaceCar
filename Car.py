import os, sys, math, pygame, pygame.mixer
import random
import euclid
from pygame.locals import *


class Car():

    def __init__(self, position, orientation):

        self.position = position # location vector 
        self.orientation = orientation # orientation vector unit vector centered at the car's origin. 
        self.velocity = 0.0 # rate of change of positon in direction of travel ms-1
        self.accel = 30.0 #Rate of change of velocity ms-2
        self.steering =  0.0005 #rate of change of yaw radm-2 -ve left, +ve right

        self.length = 30
        self.width = 20
        self.color = 0,0,0 #black
        self.line_width = 3
        self.steeringDrag = 0.3
        self.rollingDrag = 0.1

    def move(self, time_delta):
        self.position += self.velocity * self.orientation * time_delta + 0.5 * (self.accel * self.orientation * (time_delta**2))
        self.velocity += self.accel * time_delta
        self.velocity -= self.velocity * self.rollingDrag * time_delta
        self.velocity -= abs(self.steering) * self.velocity * self.steeringDrag * time_delta
        self.orientation = self.orientation.rotate_around(euclid.Vector3(0.,0.,1.),self.steering * self.velocity)

    def display(self, screen_handle):
        rx, ry = int(self.position.x), int(self.position.y)
        #pygame.draw.rect(screen_handle, self.color, (rx,ry, self.width, self.length), self.line_width)

        #get vector position of each of the corners.
        rear_left = self.position + self.orientation.rotate_around( euclid.Vector3(0.,0.,1.), -0.5*math.pi)* self.width/2 - self.orientation * 0.3*self.length
        rear_right = self.position + self.orientation.rotate_around( euclid.Vector3(0.,0.,1.), 0.5*math.pi)* self.width/2  - self.orientation * 0.3*self.length
        front_left = rear_left + self.orientation * self.length
        front_right = rear_right + self.orientation * self.length
        point_list = [(rear_left.x, rear_left.y), (front_left.x, front_left.y), (front_right.x, front_right.y), (rear_right.x, rear_right.y)]

        pygame.draw.lines(screen_handle, self.color, True, point_list, self.line_width)
        pygame.draw.circle(screen_handle, (255,0,0), (rx,ry), 2, 0)


    def control(self, acceleration, steering):
        self.accel = acceleration
        self.steering = steering



    



black = 0,0,0
white = 255,255,255
red = 255, 0, 0
green = 0, 255, 0
blue = 0, 0, 255

colors = [black,red,green,blue]

screenSize = screenWidth, screenHeight = 600, 400

# Set the screen size
screen = pygame.display.set_mode(screenSize)

clock = pygame.time.Clock()
fpsLimit = 60
runMe = True

car = Car(euclid.Vector3(300., 200., 0.), euclid.Vector3(1.,0., 0.))


while runMe:

    #get user input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            runMe = False

    #Limit the framerate
    dtime_ms = clock.tick(fpsLimit)
    dtime = dtime_ms/1000.0

    screen.fill(white)

    car.move(dtime)
    car.display(screen)

    screen.unlock()

    pygame.display.flip()

pygame.quit()
sys.exit()
         
