from keras.models import Sequential
from keras.models import Model
from keras.layers import Dense

from keras.models import model_from_json
import numpy
import random
import copy
import csv

class Network():
    #default init copies a model from input
    def __init__(self, model):
        #Init random. 
        #seed = 7
        #numpy.random.seed(seed)

        self.model = model
        self.model.compile(loss='mse', optimizer='sgd')

    #Create new model
    @classmethod
    def new(cls):
        model = Sequential()
        model.add(Dense(13, input_dim=15, init='uniform', activation='relu'))
        model.add(Dense(13, init='uniform', activation='relu'))
        model.add(Dense(13, init='uniform', activation='relu'))
        model.add(Dense(13, init='uniform', activation='relu'))
        model.add(Dense(2, init='uniform'))

        return cls(model)

    #Load model from file
    @classmethod
    def load(cls, model_file, weights_file):
        # load json and create model
        json_file = open(model_file, 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        model = model_from_json(loaded_model_json)
        # load weights into new model
        model.load_weights(weights_file)

        return cls(model)

    #Load model from config and weights
    @classmethod
    def from_config_weights(cls, config, weights):
        model = Sequential.from_config(config)
        model.set_weights(weights)
        return cls(model)

    def save(self, model_file, weights_file):
        # serialize model to JSON
        model_json = self.model.to_json()
        with open(model_file, "w") as json_file:
            json_file.write(model_json)
        # serialize weights to HDF5
        self.model.save_weights(weights_file)
        print("Saved model to disk")

    def save_weights(self, weights_file):
        self.model.save_weights(weights_file)
        print("Saved model to disk")

    def train(self, training_data, epoch=200, batch=3):
        dataset = numpy.loadtxt(training_data, delimiter=",")
        numpy.random.shuffle(dataset)

        # split into input (X) and output (Y) variables
        X = dataset[:,0:15]
        Y = dataset[:,15:]

        # Fit the model
        self.model.fit(X, Y, nb_epoch=epoch, batch_size=batch,  verbose=2)

    def predict(self, input_list):
    #Y is a lingle line list containing the inputs. 
        numpy_inputs = numpy.array([input_list])
        prediction = self.model.predict(numpy_inputs)

        #This needs to be generalized to accept any number of outputs
        return [prediction[0][0], prediction[0][1]]

    #Return the config and weights
    def get_config_weights(self):
        return copy.copy(self.model.get_config()), copy.copy(self.model.get_weights())

    #Return the config and randomly adjusted weights
    def rand_config_weights(self):
        weights = self.model.get_weights()
        weights_new = self.__mutate(weights)
        return self.model.get_config(), weights_new

    # Randomly adjust the weights of the model stored in this class
    def rand_mod(self):
        weights_new = self.__mutate(self.model.get_weights())

        self.model.set_weights(weights_new)
    
    def __mutate(self, weights):
        change_chance = random.uniform(0,1)
        for xi in range(len(weights)):
            for yi in range(len(weights[xi])):
                #if random.uniform(0, 1) > 0.3:
                if random.uniform(0, 1) > change_chance:
                    change = random.gauss(0, 0.01)
                    weights[xi][yi] += change
        return weights

#    #return a copy of this model crossed with another model
#    def model_crossover(model_idx1, model_idx2):
#        global current_pool
#        weights1 = current_pool[model_idx1].get_weights()
#        weights2 = current_pool[model_idx2].get_weights()
#        weightsnew1 = weights1
#        weightsnew2 = weights2
#        weightsnew1[0] = weights2[0]
#        weightsnew2[0] = weights1[0]
#        return np.asarray([weightsnew1, weightsnew2])
#
#        new_weights1 = model_crossover(idx1, idx2)
#        updated_weights2 = model_mutate(new_weights1[1])
#        new_weights.append(updated_weights1)
#        new_weights.append(updated_weights2)
#    for select in range(len(new_weights)):
#        fitness[select] = -100
#        current_pool[select].set_weights(new_weights[select])



