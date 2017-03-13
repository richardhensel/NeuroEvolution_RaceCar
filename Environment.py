from keras.models import model_from_json
import numpy
import euclid

import pygame.mixer
from pygame.locals import *
from pygame.key import *


import csv


class Environment():
    def __init__(self, network_list, car_list, obstacle_list, finish_line, control_type, display_option):
        
        self.network_list=network_list
        self.car_list = car_list
        self.obstacle_list = obstacle_list
        self.finish_line = finish_line
    

        self.control_type = control_type
        self.display_option = display_option

        #Limits for manual control
        self.max_accel_rate = 60.0
        self.max_steering_rate = 0.045
        
        self.max_fitness_index = 0
        self.max_fitness = 0.0
        self.max_fitness_network = self.network_list[0]
        self.max_fitness_car = self.car_list[0]



        self.all_finished = False #indicates if all cars have either crashed or finished
        self.display_index = 0 #The index of the car to follow on screen
        self.total_time = 0.0

        self.quit = False


        if len(network_list) != len(car_list):
            print "network and cars don't align"

    def control(self):
        # the first car in the list is controlled manually, others by nn
        if self.control_type == 'manual' or self.control_type == 'training':
            if self.display_option==True:
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

        #Quits the game
        if self.display_option==True:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_x] == True:
                self.quit = True
            elif keys[pygame.K_c] == True:
                self.all_finished = True

    def update(self, time_delta):
        for i in range(0,len(self.car_list)):
            if self.car_list[i].crashed != True and self.car_list[i] != True:
                self.car_list[i].update(time_delta, self.obstacle_list, self.finish_line)
        
        self.total_time += time_delta

    def display(self, screen_handle, screen_size):
        screen_vec = euclid.Vector3(screen_size[0], screen_size[1], 0.0)

        #Update the screen offset for display purposes    
        for i in range(0,len(self.car_list)):
            if self.car_list[i].crashed != True and self.car_list[i] != True:
                self.display_index = i
                break
        screen_offset_vec = 0.5 * screen_vec - self.car_list[self.display_index].position

        # Display each of the obstacles offset to the location of the first car in the list.
        for obstacle in self.obstacle_list:
            ob = []
            for point in obstacle:
                point_vec = euclid.Vector3(point[0], point[1]) + screen_offset_vec
                ob.append((point_vec.x, point_vec.y))
            pygame.draw.lines(screen_handle, (0,0,0), True, ob, 5)

        #Display each of the cars and associated lasers offset to the locatino of the first car in the list. 
        for i in range(0,len(self.car_list)):
            if i==self.display_index:
                self.car_list[i].display(screen_handle, screen_offset_vec, True)
            else:
                self.car_list[i].display(screen_handle, screen_offset_vec, False)

    def update_generation_metrics(self):
    
#        if any(True == car.finished for car in self.car_list):
#            self.all_finished = True

        if all(True == car.crashed for car in self.car_list):
            self.all_finished = True

        if self.total_time > 60:
            self.all_finished = True

        #update max fitness and leader
        for i in range(0,len(self.car_list)):
            #Update the most fit car
            if self.car_list[i].fitness > self.max_fitness:
                self.max_fitness = self.car_list[i].fitness
                self.max_fitness_index = i
                self.max_fitness_network = self.network_list[i]
                self.max_fitness_car = self.car_list[i]
