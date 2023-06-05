import random
import sys
import ast

import numpy as np
import torch

from datetime import datetime
from ML.GradientQML import GradientQML
from ML.models import classicalNN, vqc
from postgresqlJoins import PostgresqlJoins
from util.databases import ErgastF1
from util.dataformat import DataFormat
from ML import interpretation

# Default settings
settings = {
    "features": "simple",
    "encoding": "rx",
    "reuploading": False,
    "reps": 6,
    "calc": "yz",
    "entangleType": "circular",
    "entangle": "cx",
    "reward": "rational",
    "numEpisodes": 100,
    "optimizer": "SGD",
    "lr": [0.01, 100, 0.9],
    "prefix": "Loss_New",
    "noisy": False,
    "seed": 42,
    "batchsize": 1,
    "loss": "standard"
}

# update settings with command line option
if len(sys.argv) > 1:
    settings.update(ast.literal_eval(sys.argv[1]))

# init random 
random.seed(settings["seed"])
np.random.seed(settings["seed"]+1)
torch.manual_seed(settings["seed"]+2)

start_time = datetime.now()

# Create the machine learning environment
env = PostgresqlJoins(ErgastF1(), inputFile="ergastf1nC.csv", dataFormat=DataFormat(0, 1, -1))

print("Qubit Input : {}, Output: {}".format(env.getInputSize(), env.getOutputSize()))

# Create a model
model = vqc(settings=settings, num_inputs=env.getInputSize(), num_outputs=env.getOutputSize())

# Create the learning algorithm
nn = GradientQML(interpretation.fromString(settings["loss"], model), env, settings)

# Run the algorithm
nn.run()

end_time = datetime.now()
print("Duration =", end_time - start_time)

nn.listSolutions()
# print final quality
print(nn.env.elvaluateModel(nn.agent))
