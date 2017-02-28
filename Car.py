import math, pygame, pygame.mixer
import euclid
from pygame.locals import *

class Car():

    def __init__(self, position, orientation):

        # Dynamics
        self.position = position  # location vectors
        self.prev_position = position 
        self.orientation = orientation  # orientation vector unit vector centered at the car's origin. 
        self.velocity = 0.0             # rate of change of positon in direction of travel ms-1
        self.accel = 0.0               #Rate of change of velocity ms-2
        self.steering =  0.0         #rate of change of yaw radm-2 -ve left, +ve right

        #Drag parameters
        self.steeringDrag = 0.3
        self.rollingDrag = 0.1

        # Trip metrics
        self.dist_travelled = 0.0       # total distance travelled
        self.avg_velocity = 0.0         # average velocity for the trip
        self.crashed = False            # did the car crash into an obstacle?

        #Define the car geometry
        self.origin_dist = 0.25 * self.length #Origin is 1 quarter of the length from the rear of the car
        self.length = 30
        self.width = 20
        self.color = 0,0,0              #black
        self.line_width = 3

        #Define the sensor array
        self.sensor_origin_dist = 0.5
        self.sensor_length = 300.0
        self.num_sensors = 8


        #Set up NN
    

    #Geometry points
    def rear_left(self):
        return self.position + self.orientation.rotate_around( euclid.Vector3(0.,0.,1.), -0.5*math.pi)* self.width/2 - self.orientation * self.origin_dist

    def rear_right(self):
        return self.position + self.orientation.rotate_around( euclid.Vector3(0.,0.,1.), 0.5*math.pi)* self.width/2  - self.orientation * self.origin_dist

    def front_left(self):
        return self.rear_left() + self.orientation * self.length

    def front_right(self):
        return self.rear_right() + self.orientation * self.length

    def sensor_origin(self):
        return self.position + self.sensor_origin_dist * self.length * self.orientation # sensor origin is 1 quarter of the length from the front of the car

    def sensor_vectors(self):
        angle = math.pi / (self.num_sensors+1)
        vectors = []
        count = 1
        for i in range(0,self.num_sensors):
            p1 = self.sensor_origin()
            # sensor vector is count*angle radians from the right of the car, with an origin at sensor origin and a length of sensor_length 
            p2 = self.sensor_origin() + self.orientation.rotate_around(euclid.Vector3(0.,0.,1.), 0.5*math.pi - count * angle) * self.sensor_length
            vectors.append((p1,p2)) 
            count +=1
        return vectors


    def move(self, time_delta):
        self.prev_position = self.position.copy()

        self.position += self.velocity * self.orientation * time_delta + 0.5 * (self.accel * self.orientation * (time_delta**2))
        self.velocity += self.accel * time_delta
        self.velocity -= self.velocity * self.rollingDrag * time_delta
        self.velocity -= abs(self.steering) * self.velocity * self.steeringDrag * time_delta
        self.orientation = self.orientation.rotate_around(euclid.Vector3(0.,0.,1.),self.steering * self.velocity)
       
        self.dist_travelled += abs(self.position - self.prev_position)/1000.0

#    def sensor_intersect(self, obstacle):
        #Find the shortest distance to obstacle for each of the sensors

#    def detect_collision(self, obstacle):
        #Test for collision between the obstacle and each of the corners/lines of the car
        #self.crashed = True

    def display(self, screen_handle):
        rx, ry = int(self.position.x), int(self.position.y)

        #Draw car
        point_list = [(self.rear_left().x, self.rear_left().y), (self.front_left().x, self.front_left().y), (self.front_right().x, self.front_right().y), (self.rear_right().x, self.rear_right().y)]
        pygame.draw.lines(screen_handle, self.color, True, point_list, self.line_width)

        #Draw origin
        pygame.draw.circle(screen_handle, (255,0,0), (rx,ry), 2, 0)
        #Draw sensor origin
        pygame.draw.circle(screen_handle, (0,0,255), (int(self.sensor_origin().x), int(self.sensor_origin().y)), 2, 0)

        #Draw sensor vectors
        sensor_vectors = self.sensor_vectors()
        for line in sensor_vectors:
            point_list = [(line[0].x, line[0].y),(line[1].x, line[1].y)]
            pygame.draw.lines(screen_handle, (0,0,255), False, point_list, 1)    


    def control(self, acceleration, steering):
        if self.crashed == False:
            self.accel = acceleration
            self.steering = steering
