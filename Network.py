from keras.models import Sequential
from keras.layers import Dense

from keras.models import model_from_json
import numpy
import random
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
        model.add(Dense(13, input_dim=9, init='uniform', activation='relu'))
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
        X = dataset[:,0:9]
        Y = dataset[:,9:]

        # Fit the model
        self.model.fit(X, Y, nb_epoch=epoch, batch_size=batch,  verbose=2)

    def predict(self, input_list):
    #Y is a lingle line list containing the inputs. 
        numpy_inputs = numpy.array([input_list])
        prediction = self.model.predict(numpy_inputs)

        #This needs to be generalized to accept any number of outputs
        return [prediction[0][0], prediction[0][1]]

    def copy(self):
        return self.model

    def rand_mod(self):
        #model_copy = self.copy()

        weights_new = self.__mutate(self.model.get_weights())
        #for i in range(0,len(weights_new)): 
        #    weights_new[i] = self.__mutate(weights_new[i])

        self.model.set_weights(weights_new)
        #return weights_new

    
    def __mutate(self, weights):
        for xi in range(len(weights)):
            for yi in range(len(weights[xi])):
                if random.uniform(0, 1) > 0.9:
                    change = random.uniform(-0.05,0.05)
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



