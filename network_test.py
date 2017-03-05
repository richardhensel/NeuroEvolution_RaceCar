from Network import Network
import numpy

network = Network.load("model.json", "model.h5")

weights = network.model.get_weights()

print weights
#n = numpy.random.binomial(len(a), 0.1)
#a[numpy.random.randint(0, len(a), size=n)] *= 1.1
