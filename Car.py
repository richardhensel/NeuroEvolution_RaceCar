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
        self.total_time = 0.0
        self.avg_velocity = 0.0         # average velocity for the trip
        self.crashed = False            # did the car crash into an obstacle?

        #Define the car geometry
        self.length = 30
        self.width = 20
        self.origin_dist = 0.25 * self.length #Origin is 1 quarter of the length from the rear of the car
        self.color = 0,0,0              #black
        self.line_width = 3

        #Define the sensor array
        self.sensor_origin_dist = 0.5
        self.max_sensor_length = 300.0
        self.num_sensors = 8
        self.sensor_measurements = [self.max_sensor_length] * self.num_sensors

        #Set up NN
    
    def __update_geometry(self):
    #Geometry points
        self.rear_left = self.position + self.orientation.rotate_around( euclid.Vector3(0.,0.,1.), -0.5*math.pi)* self.width/2 - self.orientation * self.origin_dist
        self.rear_right = self.position + self.orientation.rotate_around( euclid.Vector3(0.,0.,1.), 0.5*math.pi)* self.width/2  - self.orientation * self.origin_dist
        self.front_left = self.rear_left + self.orientation * self.length
        self.front_right = self.rear_right + self.orientation * self.length
        self.sensor_origin = self.position + self.sensor_origin_dist * self.length * self.orientation # sensor origin is 1 quarter of the length from the front of the car

    def __get_sensor_vectors(self, ray_lengths):
        angle = math.pi / (self.num_sensors+1)
        vectors = []
        count = 1
        for i in range(0,self.num_sensors):
            p1 = self.sensor_origin
            # sensor vector is count*angle radians from the right of the car, with an origin at sensor origin and a length of sensor_length 
            p2 = self.sensor_origin + self.orientation.rotate_around(euclid.Vector3(0.,0.,1.), 0.5*math.pi - count * angle) * ray_lengths[i]

            vectors.append((p1,p2)) 
            count +=1
        return vectors

    def move(self, time_delta):
        if self.crashed ==True:
            self.velocity = 0.0
            self.accel = 0.0

        self.position += self.velocity * self.orientation * time_delta + 0.5 * (self.accel * self.orientation * (time_delta**2))
        self.velocity += self.accel * time_delta
        self.velocity -= self.velocity * self.rollingDrag * time_delta
        self.velocity -= abs(self.steering) * self.velocity * self.steeringDrag * time_delta
        self.orientation = self.orientation.rotate_around(euclid.Vector3(0.,0.,1.),self.steering * self.velocity)
      
        if self.crashed != True: 
            self.dist_travelled += abs(self.position - self.prev_position)/1000.0
            self.total_time += time_delta
            self.avg_velocity = self.dist_travelled/self.total_time
            print self.dist_travelled , self.total_time, self.avg_velocity

        self.prev_position = self.position.copy()

        self.__update_geometry()

    def get_line_intersection(self, p1, p2, p3, p4):
        s1 = (p2[0] - p1[0], p2[1] - p1[1])
        s2 = (p4[0] - p3[0], p4[1] - p3[1])

        s = (-s1[1] * (p1[0] - p3[0]) + s1[0] * (p1[1] - p3[1])) / (-s2[0] * s1[1] + s1[0] * s2[1]);
        t = ( s2[0] * (p1[1] - p3[1]) - s2[1] * (p1[0] - p3[0])) / (-s2[0] * s1[1] + s1[0] * s2[1]);

        if (s >= 0 and s <= 1 and t >= 0 and t <= 1):

            i_x = p1[0] + (t * s1[0])
            i_y = p1[1] + (t * s1[1])
            return i_x, i_y # Collision detected
        else:
            return None, None # No collision

    def sense(self, obstacle):
#        self.sensor_ranges = []
        sensor_vectors = self.__get_sensor_vectors([self.max_sensor_length] * self.num_sensors)
        for i in range(0,len(sensor_vectors)):
            intersect_list = []
#            min_range = self.sensor_length

            ray = sensor_vectors[i]
            #unpack the start and end points of the sensor ray
            p1 = (ray[0].x, ray[0].y)
            p2 = (ray[1].x, ray[1].y)
            for j in range(0,len(obstacle)):
                if j ==0:
                    p3 = obstacle[-1]
                else:
                    p3 = obstacle[j-1]
                p4 = obstacle[j]
                #Get intersection point in global frame
                ix, iy = self.get_line_intersection(p1, p2, p3, p4)
                #Append all non-null intersections to the list of intersections for that ray
                if ix != None and iy != None:
                    intersect_list.append(euclid.Vector3(ix,iy, 0.0))
            # find the minimum distance. range must be shorter than the current stored min range to be stored. 
            for vector in intersect_list:
                measured_range = abs(vector - ray[0])
                if measured_range < self.sensor_measurements[i]:
                    self.sensor_measurements[i] = measured_range
        #print self.sensor_measurements
    def detect_collision(self, obstacle):
        car_bounds = [self.rear_left, self.front_left, self.front_right, self.rear_right]
        for i in range(0,len(car_bounds)):
            if i ==0:
                p1 = car_bounds[-1]
            else:
                p1 = car_bounds[i-1]
            p2 = car_bounds[i]

            for j in range(0,len(obstacle)):
                if j ==0:
                    p3 = obstacle[-1]
                else:
                    p3 = obstacle[j-1]
                p4 = obstacle[j]
                
                #Get intersection point in global frame
                ix, iy = self.get_line_intersection(p1, p2, p3, p4)
                if ix != None or iy != None:
                    self.crashed = True
                    return 0
                    
        
        #Test for collision between the obstacle and each of the corners/lines of the car
        #self.crashed = True

    def display(self, screen_handle):
        rx, ry = int(self.position.x), int(self.position.y)

        #Draw car
        point_list = [(self.rear_left.x, self.rear_left.y), (self.front_left.x, self.front_left.y), (self.front_right.x, self.front_right.y), (self.rear_right.x, self.rear_right.y)]
        pygame.draw.lines(screen_handle, self.color, True, point_list, self.line_width)

        #Draw origin
        pygame.draw.circle(screen_handle, (255,0,0), (rx,ry), 2, 0)
        #Draw sensor origin
        pygame.draw.circle(screen_handle, (0,0,255), (int(self.sensor_origin.x), int(self.sensor_origin.y)), 2, 0)

        #Draw sensor vectors
        sensor_vectors = self.__get_sensor_vectors(self.sensor_measurements)
        for line in sensor_vectors:
            point_list = [(line[0].x, line[0].y),(line[1].x, line[1].y)]
            pygame.draw.lines(screen_handle, (0,0,255), False, point_list, 1)    

        #Draw sensor intersects
        #for point in self.vector_list:
        #    pygame.draw.circle(screen_handle, (255,0,0), (int(point[0]), int(point[1])), 2, 0)
    
    def reset_sensors(self):
        self.sensor_measurements = [self.max_sensor_length] * self.num_sensors

    def control(self, acceleration, steering):
        if self.crashed == False:
            self.accel = acceleration
            self.steering = steering
