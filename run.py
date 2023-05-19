import sys
import ast

from datetime import datetime
from ML.GradientQML import GradientQML
from ML.Genetic import GeneticAlgorithm
from ML.models import classicalNN, vqc
from postgresqlJoins import PostgresqlJoins
from util.databases import ErgastF1
from util.dataformat import DataFormat
from ML import interpretation

settings = {
    "features": "simple",
    "encoding": "rx",
    "reuploading": False,
    "reps": 20,
    "calc": "yz",
    "entangleType": "circular",
    "entangle": "cx",
    "reward": "rational",
    "numEpisodes": 8000,
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

start_time = datetime.now()

env = PostgresqlJoins(ErgastF1(), inputFile="ergastf1nC.csv", dataFormat=DataFormat(0, 1, -1))

print("Qubit Input : {}, Output: {}".format(env.getInputSize(), env.getOutputSize()))

# use quantum model
model = vqc(settings=settings, num_inputs=env.getInputSize(), num_outputs=env.getOutputSize())

# use classical model
# model = classicalNN()

# select the algorithm
#nn = GeneticAlgorithm(model,{"numEpisodes":40,"lr":0.001})
nn = GradientQML(interpretation.fromString(settings["loss"], model), env, settings)
#nn = GeneticAlgorithm(model,env,settings)

nn.run()

end_time = datetime.now()
print("Duration =", end_time - start_time)

nn.listSolutions()
print(nn.env.elvaluateModel(nn.agent))
