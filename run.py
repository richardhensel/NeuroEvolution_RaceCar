import os, sys, math, pygame, pygame.mixer
import random
import euclid
from pygame.locals import *
from pygame.key import *

from keras.models import model_from_json
import numpy

import csv  
from Car import Car
from Network import Network
from Environment import Environment

screenSize = screenWidth, screenHeight = 1000, 700

# Set the screen size
screen = pygame.display.set_mode(screenSize)

clock = pygame.time.Clock()
fpsLimit = 60
runMe = True

left_barrier = [(980, 20), (1000.0, 20.0), (980, 20), (980, 20), (980, 20), (980, 20), (980, 20), (980, 20), (980, 20), (980, 20), (980, 20), (980, 20), (980, 20), (980, 20), (980, 20), (980, 20), (980, 20), (980, 20), (980, 20), (980, 20), (980, 20), (980, 20), (981, 20), (995, 19), (1023, 20), (1065, 25), (1120, 33), (1189, 37), (1267, 33), (1341, 45), (1411, 63), (1479, 72), (1542, 65), (1603, 60), (1662, 60), (1714, 80), (1752, 118), (1771, 164), (1772, 212), (1762, 256), (1746, 296), (1730, 333), (1717, 371), (1718, 417), (1737, 456), (1766, 484), (1799, 504), (1832, 523), (1860, 556), (1875, 598), (1874, 641), (1863, 685), (1840, 728), (1805, 779), (1769, 839), (1735, 903), (1696, 973), (1641, 1038), (1569, 1084), (1489, 1106), (1409, 1104), (1338, 1083), (1277, 1046), (1229, 997), (1196, 941), (1176, 882), (1163, 824), (1153, 769), (1137, 718), (1116, 672), (1090, 631), (1058, 593), (1026, 554), (995, 513), (955, 479), (905, 467), (854, 480), (812, 509), (783, 548), (761, 589), (739, 634), (717, 683), (700, 731), (679, 774), (653, 811), (623, 841), (590, 866), (555, 886), (510, 901), (459, 910), (410, 909), (359, 909), (309, 911), (257, 909), (204, 896), (157, 866), (130, 820), (119, 771), (117, 723), (112, 677), (100, 632), (86, 585), (81, 537), (79, 487), (78, 433), (83, 374), (106, 318), (153, 280), (212, 273), (272, 277), (333, 264), (377, 225), (396, 172), (405, 119), (425, 72), (462, 40), (505, 25), (548, 21), (590, 20), (632, 21), (674, 20), (713, 15), (750, 12), (789, 11), (829, 12), (869, 17), (910, 18)]

right_barrier = [(980, 120), (1000.0, 120.0), (980, 120), (984, 120), (1002, 120), (1028, 119), (1068, 120), (1122, 122), (1186, 123), (1250, 126), (1309, 136), (1363, 156), (1414, 170), (1466, 168), (1514, 166), (1560, 172), (1598, 196), (1623, 232), (1632, 271), (1625, 308), (1611, 341), (1599, 372), (1592, 406), (1592, 439), (1599, 471), (1612, 498), (1629, 522), (1645, 545), (1658, 567), (1675, 585), (1692, 602), (1705, 622), (1714, 650), (1716, 679), (1710, 707), (1695, 734), (1673, 755), (1653, 777), (1638, 802), (1624, 828), (1610, 856), (1594, 887), (1570, 917), (1537, 937), (1498, 953), (1458, 957), (1419, 951), (1384, 930), (1357, 901), (1339, 866), (1328, 827), (1318, 789), (1305, 754), (1294, 719), (1278, 683), (1260, 649), (1241, 613), (1223, 578), (1203, 541), (1182, 505), (1159, 470), (1138, 437), (1114, 406), (1089, 380), (1067, 353), (1043, 331), (1013, 314), (981, 304), (946, 304), (912, 312), (879, 326), (851, 347), (833, 374), (820, 402), (802, 425), (780, 443), (755, 462), (728, 478), (701, 498), (674, 519), (649, 541), (628, 569), (606, 599), (585, 627), (563, 655), (541, 688), (518, 720), (490, 751), (457, 781), (417, 804), (372, 811), (329, 805), (291, 791), (257, 771), (232, 743), (219, 707), (216, 669), (219, 631), (224, 593), (227, 556), (228, 519), (233, 480), (247, 443), (269, 409), (298, 382), (331, 366), (365, 356), (399, 353), (430, 346), (457, 332), (477, 311), (493, 288), (500, 263), (505, 239), (511, 216), (520, 195), (537, 174), (559, 156), (587, 145), (618, 140), (650, 137), (684, 138), (719, 135), (754, 129), (792, 124), (827, 118), (861, 113), (893, 111), (924, 112)]


car_x = 1000.0
car_y = 80.0

#control_option = 'training'
#control_option = 'manual'
#control_option = 'neural'
control_option = 'reinforcement'
training_data = 'training_data.csv'
generation_file = 'generation.csv'

num_cars = 20

def get_generation(gen_file):
    generation = 0
    with open(gen_file, 'rb') as f:
        reader = csv.reader(f, delimiter=',')
        for line in reader:
            generation = int(line[0]) 
            print generation
    
    return generation

def set_generation(gen_file, generation):
    #Write data set to csv
    with open(gen_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerow([generation])


while runMe:

    #load the generation number
    if control_option == 'reinforcement':
        generation = get_generation(generation_file)+1 #increment the generation by 1 
    else:
        generation = 0

    dirn = random.randint(0,1)
    if  dirn == 1:
        direction = 1.0
    else:
        direction = -1.0

    model_file = 'model/model.json'
    weights_file = 'model/weights_gen'+str(generation)+'.h5'
    initial_network = Network.load(model_file, weights_file)

    network_list = []
    car_list = []
    for i in range(num_cars):
    
        config, weights = initial_network.rand_config_weights()
        network_list.append(Network.from_config_weights(config, weights))

        car_list.append(Car(euclid.Vector3(car_x, car_y, 0.), euclid.Vector3(direction,0., 0.)))

    for car in car_list:
    #Start with initial acceleration
        car.control_unscaled(60.0, 0.0)

    obstacles = [left_barrier,right_barrier]

    finish_line = [(car_x-10.0, car_y - 100), (car_x-10.0, car_y + 100)]

    environment = Environment(network_list, car_list, obstacles, finish_line, screen, screenSize, control_option)

   ## NEEDED TO TRACE A LINE ON SCREEN
   # points = []
   # pos = car.position
   # orient = car.orientation
   # pos_behind = pos - orient * 20.0
   # points.append((int(pos_behind.x), int(pos_behind.y)))
   # points.append((car_x, car_y))

    while runMe == True:

        #get user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                runMe = False



        screen.fill((255,255,255))

        environment.control()

        #Limit the framerate
        dtime_ms = clock.tick(fpsLimit)
        #dtime_ms = clock.tick()
        #dtime = dtime_ms/1000.0

        dtime = 0.1

        environment.update(dtime)
        environment.display()

        ## NEEDED TO TRACE A LINE ON SCREEN
       # timer += dtime
       # if timer - old_timer > clock_tick:
       #    pos = car.position
       #    orient = car.orientation
       #    pos_behind = pos - orient * 20.0

       #    points.append((int(pos_behind.x), int(pos_behind.y)))

       #    #print (pos_behind.x, pos_behind.y)
       #    old_timer = timer

        screen.unlock()
        pygame.display.flip()

        if environment.check_finished() == True:
            if control_option == 'training': 
                car = environment.car_list[0]
                if car.finished:
                    print 'MANUAL FINISHED! Distance = ', car.dist_travelled,  ' Time = ', car.total_time, 'velocity = ', car.avg_velocity
                    car.write_data(training_data)


            elif control_option == 'reinforcement':
                best_model = environment.network_list[environment.max_dist_index]
                weights_file = 'model/weights_gen'+str(generation)+'.h5'
                best_model.save_weights(weights_file)

                #Set the generation file for next loop
                set_generation(generation_file, generation+1)
                #get the most fit car
                #save the model weights to file   
            break
       # if car.finished==True:
       #     print 'FINISHED! Distance = ', car.dist_travelled,  ' Time = ', car.total_time, 'velocity = ', car.avg_velocity

       #     if control_option == 'training': 
       #         #Write data set to csv
       #         with open(training_data, 'a') as f:
       #             writer = csv.writer(f)
       #             for line in car.data_log:
       #                 writer.writerow(line)
       #         print "Training data written to file"    
       #     break
       # if car.crashed==True:
       #     print 'CRASHED! Distance = ', car.dist_travelled,  ' Time = ', car.total_time, 'velocity = ', car.avg_velocity
       #     break
        ## NEEDED TO TRACE A LINE ON SCREEN
    #print points
pygame.quit()
sys.exit()


