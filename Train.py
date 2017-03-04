
from Network import Network

network = Network.load("model.json", "model.h5")

network.train("training_data.csv", epoch=200, batch=3)

network.save("testmodel.json", "testmodel.h5")



