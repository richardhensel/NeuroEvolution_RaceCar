from Network import Network

#network = Network.load("model.json", "model.h5")
network = Network.new()

#network.train("training/training_data.csv", epoch=30, batch=3)


network.save("model/model.json", "model/weights_gen0.h5")
