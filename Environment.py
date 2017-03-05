from keras.models import model_from_json
import numpy
import euclid

import pygame.mixer
from pygame.locals import *
from pygame.key import *


import csv


class Environment():
    def __init__(self, network_list, car_list, obstacle_list, finish_line, screen_handle, screen_size, control_type):
        
        self.network_list=network_list
        self.car_list = car_list
        self.obstacle_list = obstacle_list
        self.finish_line = finish_line
    
        self.screen_handle = screen_handle
        self.screen_vec = euclid.Vector3(screen_size[0], screen_size[1], 0.0)

        self.control_type = control_type
        #Limits for manual control
        self.max_accel_rate = 60.0
        self.max_steering_rate = 0.03
        
        self.max_dist_index = 0
        self.all_complete = False #indicates if all cars have either crashed or finished

        self.total_time = 0.0

        if len(network_list) != len(car_list):
            print "network and cars don't align"

    def control(self):
        # the first car in the list is controlled manually, others by nn
        if self.control_type == 'manual' or self.control_type == 'training':
            keys = pygame.key.get_pressed()
            if (keys[pygame.K_a] ==True and keys[pygame.K_f] ==True) or (keys[pygame.K_a] ==False and keys[pygame.K_f] ==False):
                steering_rate = 0.0
            elif keys[pygame.K_a] ==True:
                steering_rate = -1 * self.max_steering_rate
            elif keys[pygame.K_f] ==True:
                steering_rate = self.max_steering_rate

            if (keys[pygame.K_UP] ==True and keys[pygame.K_DOWN] ==True) or (keys[pygame.K_UP] ==False and keys[pygame.K_DOWN] ==False):
                accel_rate = 0.0
            elif keys[pygame.K_UP] ==True:
                accel_rate = self.max_accel_rate
            elif keys[pygame.K_DOWN] ==True:
                accel_rate = -1 * self.max_accel_rate

            self.car_list[0].control_rates(accel_rate, steering_rate)

            #prediction = self.network_list[0].predict(self.car_list[0].get_inputs())
            #self.car_list[0].control_scaled(prediction[0], prediction[1])

            if len(self.car_list) > 1:
                for i in range(1,len(self.car_list)):
                    if self.car_list[i].crashed != True and self.car_list[i].finished != True:
                        prediction = self.network_list[i].predict(self.car_list[i].get_inputs())
                        self.car_list[i].control_scaled(prediction[0], prediction[1])

        #All cars controlled by nn
        #elif self.control_type == 'neural':
        else:
            for i in range(0,len(self.car_list)):
                if self.car_list[i].crashed != True and self.car_list[i].finished != True:
                    prediction = self.network_list[i].predict(self.car_list[i].get_inputs())
                    self.car_list[i].control_scaled(prediction[0], prediction[1])

    def update(self, time_delta):
        for i in range(0,len(self.car_list)):
            if self.car_list[i].crashed != True and self.car_list[i] != True:
                self.car_list[i].update(time_delta, self.obstacle_list, self.finish_line)
        
        #Update the screen offset for display purposes    
        for i in range(0,len(self.car_list)):
            if self.car_list[i].crashed != True and self.car_list[i] != True:
                self.screen_offset_vec = 0.5 * self.screen_vec - self.car_list[i].position
                break

        self.total_time += time_delta

    def display(self):

        # Display each of the obstacles offset to the location of the first car in the list.
        for obstacle in self.obstacle_list:
            ob = []
            for point in obstacle:
                point_vec = euclid.Vector3(point[0], point[1]) + self.screen_offset_vec
                ob.append((point_vec.x, point_vec.y))
            pygame.draw.lines(self.screen_handle, (0,0,0), True, ob, 5)

        #Display each of the cars and associated lasers offset to the locatino of the first car in the list. 
        for i in range(0,len(self.car_list)):
            if i==0:
                self.car_list[i].display(self.screen_handle, self.screen_offset_vec, False)
            else:
                self.car_list[i].display(self.screen_handle, self.screen_offset_vec, False)
    def check_finished(self):
        finished = False
        for car in self.car_list:
            if car.finished == True:
                finished = True
                break
            if car.crashed == False and car.finished == False:
                return False

        if self.total_time > 60:
            finished = True

        if finished == True:
            #get best index
            max_dist = 0
            for i in range(0,len(self.car_list)):
                if self.car_list[i].dist_travelled > max_dist:
                    max_dist = self.car_list[i].dist_travelled
                    self.max_dist_index = i
        return finished


