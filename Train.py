
from Network import Network

network = Network.load("model.json", "model.h5")

network.train("training_data.csv", nb_epoch=5, batch_size=3,  verbose=2)

network.save("testmodel.json", "testmodel.h5")



