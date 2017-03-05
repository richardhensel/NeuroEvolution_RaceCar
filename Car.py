import math, pygame, pygame.mixer
import euclid
from pygame.locals import *

import csv

class Car():

    def __init__(self, position, orientation):

        # Dynamics
        self.position = position  # location vectors
        self.prev_position = position 
        self.orientation = orientation  # orientation vector unit vector centered at the car's origin. 
        self.velocity = 0.0             # rate of change of positon in direction of travel ms-1

        self.accel = 0.0               #Rate of change of velocity ms-2
        self.accel_rate = 0.0           #Rate of change of accel ms-3

        self.steering =  0.0         #rate of change of yaw with respect to velocity rad/pixel -ve left, +ve right
        self.steering_rate =  0.0         #rate of change of steering rad/pixel/second -ve left, +ve right

        #Limits    
        self.max_velocity = 400.0
        self.max_accel = 100.0     
        #self.max_steering = 0.00015 #For orientation not dependant on dtime.
        self.max_steering = 0.009 #Works well for manual control

        #Drag parameters
        self.steering_drag = 0.9
        self.rolling_drag = 0.1

        # Trip metrics
        self.dist_travelled = 0.0       # total distance travelled
        self.total_time = 0.0
        self.avg_velocity = 0.0         # average velocity for the trip
        self.crashed = False            # did the car crash into an obstacle?
        self.finished = False            # did the car pass through the finish line? 

        #Define the car geometry
        self.length = 30   #pixels
        self.width = 20    #pixels 
        self.origin_dist = 0.25 * self.length #Origin is 1 quarter of the length from the rear of the car
        self.color = 0,0,0              #black
        self.line_width = 3

        #Define the sensor array
        self.sensor_origin_dist = 0.5
        self.max_sensor_length = 500.0
        self.num_sensors = 8
        self.sensor_ranges = [self.max_sensor_length] * self.num_sensors

        self.screen_offset_vec = euclid.Vector3(0.0, 0.0, 0.0)

        self.data_log = []

    def get_inputs(self):
        inputs = []
        #Inputs
        for s_range in self.sensor_ranges:
            inputs.append(self.__truncate(s_range,2))

        inputs.append(self.__truncate(self.velocity,2))
        return inputs 

    def control_scaled(self, accel_scaled, steer_scaled):
        if self.crashed == False:
            self.accel = self.__translate(accel_scaled, -1.0, 1.0, -1*self.max_accel, self.max_accel)
            self.steering = self.__translate(steer_scaled, -1.0, 1.0, -1*self.max_steering, self.max_steering)

    def control_unscaled(self, accel, steering):
        if self.crashed == False:
            self.accel = accel
            self.steering = steering

    def control_rates(self, accel_rate, steering_rate):
        if self.crashed == False:
            self.accel_rate = accel_rate
            self.steering_rate = steering_rate

    def update(self, time_delta, obstacles, finish_line):
        self.__reset_sensors()
        self.__update_dynamics(time_delta)
        self.__update_geometry()

        for obstacle in obstacles:
            self.__sense(obstacle)
            self.__detect_collision(obstacle)
        self.__detect_finish_line(finish_line)

        self.__log_data(False, True)

    def __translate(self, value, leftMin, leftMax, rightMin, rightMax):
        self.data_log.append(current_data)

    def display(self, screen_handle, screen_offset_vec, draw_vectors = True):
        #Compute offsets

        pos = self.position + screen_offset_vec

        rl = self.rear_left + screen_offset_vec
        fl = self.front_left + screen_offset_vec
        fr = self.front_right + screen_offset_vec
        rr = self.rear_right + screen_offset_vec
        
        so = self.sensor_origin + screen_offset_vec
    
        sensor_vectors = self.__get_sensor_vectors(self.sensor_ranges)
        sv = []
        for line in sensor_vectors:
            sv.append((line[0]+screen_offset_vec, line[1]+screen_offset_vec))

        #Draw car

        #Draw the offset points
        point_list = [(rl.x, rl.y), (fl.x, fl.y), (fr.x, fr.y), (rr.x, rr.y)]
        pygame.draw.lines(screen_handle, self.color, True, point_list, self.line_width)

        #Draw origin
        pygame.draw.circle(screen_handle, (255,0,0), (int(pos.x),int(pos.y)), 2, 0)
        #Draw sensor origin
        #pygame.draw.circle(screen_handle, (0,0,255), (int(so.x), int(so.y)), 2, 0)

        #Draw sensor vectors
        if draw_vectors == True:
            for line in sv:
                point_list = [(line[0].x, line[0].y),(line[1].x, line[1].y)]
                pygame.draw.lines(screen_handle, (0,0,255), False, point_list, 1)

            #Draw the intersection if detected
            #pygame.draw.circle(screen_handle, (255,0,0), (int(line[1].x), int(line[1].y)), 2, 0)

    def write_data(self, file_name):
        #Write data set to csv
        with open(file_name, 'a') as f:
            writer = csv.writer(f)
            for line in self.data_log:
                writer.writerow(line)
        print "Training data written to file"

    def __truncate(self, f, n):
        '''Truncates/pads a float f to n decimal places without rounding'''
        s = '{}'.format(f)
        if 'e' in s or 'E' in s:
            return '{0:.{1}f}'.format(f, n)
        i, p, d = s.partition('.')
        return '.'.join([i, (d+'0'*n)[:n]])


    def __reset_sensors(self):
        self.sensor_ranges = [self.max_sensor_length] * self.num_sensors

    def __update_dynamics(self, time_delta):
        # stay still if crashed
        if self.crashed ==True:
            self.velocity = 0.0
            self.accel = 0.0

        # store previous position for distance accumulation
        self.prev_position = self.position.copy()

        # update rates
        self.steering += self.steering_rate * time_delta
        if self.steering > self.max_steering:
            self.steering = self.max_steering
        elif self.steering < -1*self.max_steering:
            self.steering = -1*self.max_steering

        self.accel += self.accel_rate * time_delta
        if self.accel > self.max_accel:
            self.accel = self.max_accel
        elif self.accel < -1*self.max_accel:
            self.accel = -1*self.max_accel

        self.velocity += self.accel * time_delta
        self.velocity -= self.velocity * self.rolling_drag * time_delta
        self.velocity -= self.velocity * abs(self.steering) * self.steering_drag * time_delta
        if self.velocity > self.max_velocity:
            self.velocity = self.max_velocity
        elif self.velocity < -1*self.max_velocity:
            self.velocity = -1*self.max_velocity

        # update pose
        self.orientation = self.orientation.rotate_around(euclid.Vector3(0.,0.,1.),self.steering * self.velocity * time_delta + 0.5 * (self.steering_rate * (time_delta**2)))
        self.position += self.velocity * self.orientation * time_delta + 0.5 * (self.accel * self.orientation * (time_delta**2))
        
        # Accumulate trip metrics
        if self.crashed == False: 
            self.dist_travelled += math.copysign(abs(self.position - self.prev_position), self.velocity)
            self.total_time += time_delta
            self.avg_velocity = self.dist_travelled/self.total_time

    def __update_geometry(self):
    #Geometry points
        self.rear_left = self.position + self.orientation.rotate_around( euclid.Vector3(0.,0.,1.), -0.5*math.pi)* self.width/2 - self.orientation * self.origin_dist
        self.rear_right = self.position + self.orientation.rotate_around( euclid.Vector3(0.,0.,1.), 0.5*math.pi)* self.width/2  - self.orientation * self.origin_dist
        self.front_left = self.rear_left + self.orientation * self.length
        self.front_right = self.rear_right + self.orientation * self.length
        self.sensor_origin = self.position + self.sensor_origin_dist * self.length * self.orientation # sensor origin is 1 quarter of the length from the front of the car

    def __sense(self, obstacle):
        sensor_vectors = self.__get_sensor_vectors([self.max_sensor_length] * self.num_sensors)
        for i in range(0,len(sensor_vectors)):
            intersect_list = []

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
                ix, iy = self.__get_line_intersection(p1, p2, p3, p4)
                #Append all non-null intersections to the list of intersections for that ray
                if ix != None and iy != None:
                    intersect_list.append(euclid.Vector3(ix,iy, 0.0))
            # find the minimum distance. range must be shorter than the current stored min range to be stored. 
            for vector in intersect_list:
                measured_range = abs(vector - ray[0])
                if measured_range < self.sensor_ranges[i]:
                    self.sensor_ranges[i] = measured_range
        #print self.sensor_ranges

    def __detect_collision(self, obstacle):
        car_bounds = [self.rear_left, self.front_left, self.front_right, self.rear_right]
        for i in range(0,len(car_bounds)):
            if i ==0:
                p1 = (car_bounds[-1].x, car_bounds[-1].y)
            else:
                p1 = (car_bounds[i-1].x, car_bounds[i-1].y)
            p2 = (car_bounds[i].x, car_bounds[i].y)

            for j in range(0,len(obstacle)):
                if j ==0:
                    p3 = obstacle[-1]
                else:
                    p3 = obstacle[j-1]
                p4 = obstacle[j]
               
                #Get intersection point in global frame
                ix, iy = self.__get_line_intersection(p1, p2, p3, p4)
                if ix != None or iy != None:
                    self.crashed = True
                    return 0
                    
    def __detect_finish_line(self, finish_line):

        finish_bar = self.sensor_origin + self.orientation * 5.0
        p1 = (self.sensor_origin.x, self.sensor_origin.y)
        p2 = (finish_bar.x, finish_bar.y)

        for j in range(0,len(finish_line)):
            if j ==0:
                p3 = finish_line[-1]
            else:
                p3 = finish_line[j-1]
            p4 = finish_line[j]
           
            #Get intersection point in global frame
            ix, iy = self.__get_line_intersection(p1, p2, p3, p4)
            if ix != None or iy != None:
                self.finished = True
                return 0
        
        #Test for collision between the obstacle and each of the corners/lines of the car
        #self.crashed = True

    def __log_data(self, scale_inputs, scale_outputs):
        # Scale the data to values between -1 and 1. append to list with one row per time step
        current_data = []
        #Inputs
        if scale_inputs:
            for s_range in self.sensor_ranges:
                current_data.append(self.__truncate(self.__translate(s_range, 0.0, self.max_sensor_length, 0.0, 1.0),2))

            current_data.append(self.__truncate(self.__translate(self.velocity, 0.0, self.max_velocity, 0.0, 1.0),2))
        else:
            for s_range in self.sensor_ranges:
                current_data.append(self.__truncate(s_range,2))

            current_data.append(self.__truncate(self.velocity,2))

        if scale_outputs:
            current_data.append(self.__truncate(self.__translate(self.accel, -1* self.max_accel, self.max_accel, -1.0, 1.0),2))
            current_data.append(self.__truncate(self.__translate(self.steering, -1* self.max_steering, self.max_steering, -1.0, 1.0),2))
        else:
        #Outputs
            current_data.append(self.__truncate(self.accel,2))
            current_data.append(self.__truncate(self.steering,2))

        self.data_log.append(current_data)
    
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


    def __get_line_intersection(self, p1, p2, p3, p4):
        try:
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
        except:
            return None, None

    def __translate(self, value, leftMin, leftMax, rightMin, rightMax):
        # Figure out how 'wide' each range is
        leftSpan = leftMax - leftMin
        rightSpan = rightMax - rightMin

        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value - leftMin) / float(leftSpan)

        # Convert the 0-1 range into a value in the right range.
        return rightMin + (valueScaled * rightSpan)
