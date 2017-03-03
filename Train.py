import csv

import numpy 
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasRegressor
from keras.optimizers import SGD
from keras.models import model_from_json

from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

#keras.optimizers.SGD(lr=0.005, momentum=0.0, decay=0.0, nesterov=False)

#sgd = SGD(lr=0.03, decay=1e-6, momentum=0.9, nesterov=True)

#Init random. 
seed = 7
numpy.random.seed(seed)

def new_model():
    model = Sequential()
    model.add(Dense(13, input_dim=9, init='uniform', activation='relu'))
    model.add(Dense(13, init='uniform', activation='relu'))
    model.add(Dense(13, init='uniform', activation='relu'))
    model.add(Dense(13, init='uniform', activation='relu'))
    model.add(Dense(2, init='uniform'))
    #Compile the model.
    model.compile(loss='mse', optimizer='sgd', metrics=['mape'])
    return model

def load_model():
    # load json and create model
    json_file = open('model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)
    # load weights into new model
    model.load_weights("model.h5")
    model.compile(loss='mse', optimizer='sgd', metrics=['mape'])
    return model

dataset = numpy.loadtxt("training_data.csv", delimiter=",")
numpy.random.shuffle(dataset)

# split into input (X) and output (Y) variables
X = dataset[:,0:9]
Y = dataset[:,9:]


model = new_model()
#model = load_model()

# Fit the model
model.fit(X, Y, nb_epoch=100, batch_size=3,  verbose=2)


# serialize model to JSON
model_json = model.to_json()
with open("model.json", "w") as json_file:
    json_file.write(model_json)
# serialize weights to HDF5
model.save_weights("model.h5")
print("Saved model to disk")
#
#
## evaluate the model
#scores = model.evaluate(X, Y, verbose=0)
#print scores
#
# load json and create model
#json_file = open('model.json', 'r')
#loaded_model_json = json_file.read()
#json_file.close()
#model = model_from_json(loaded_model_json)
## load weights into new model
#model.load_weights("model.h5")
#print("Loaded model from disk")



#prediction = model.predict(numpy.expand_dims(X[0], axis=0))
#print prediction



