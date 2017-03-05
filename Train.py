
from Network import Network

network = Network.load("model.json", "model.h5")

network.train("training/training_data.csv", epoch=30, batch=3)

network.save("model2.json", "model2.h5")



