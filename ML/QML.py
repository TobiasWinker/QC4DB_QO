import numpy as np
import torch
import random

from ML.interpretation import Interpretation
from postgresqlJoins import PostgresqlJoins


class QML:

    # default settings
    settings = {"features": "simple", "encoding": "rx", "reuploading": False, "reps": 5, "calc": "yz", "entangleType": "circular", "entangle": "cx", "reward": "rational", "numEpisodes": 40, "optimizer": "sgd", "lr": 0.001, "prefix": "test", "seed": 42}

    agent: Interpretation
    env: PostgresqlJoins

    # Fix seed for reproducibility
    def __init__(self, agent, env, settings, inputFile="data.csv"):
        self.settings.update(settings)
        self.agent = agent
        self.env = env

        seed = self.settings["seed"]
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)

        self.logInterval = 100
        self.numEpisodes = self.settings["numEpisodes"]

        # logging files
        self.prefix = self.settings["prefix"] + self.prefix
        self.baseDir = "results"
        self.outputFilename = self.prefix + "_" + "_".join(str(e) for e in self.settings.values())
        self.resultFile = open(self.generateFilename(".", "csv"), "w")
        self.resultFile.write("ep, linear, log, rational, nBest, nWorst, nWrong, nCross \n")

    def generateFilename(self, folder, postfix):
        return self.baseDir + "/" + folder + "/" + self.outputFilename + "." + postfix

    def run(self):
        pass

    def listSolutions(self):
        file = open(self.generateFilename("solutions", "sl.csv"), "w")
        file.write("id, selected, reward\n")
        solutions = self.env.listSolutions(self.agent)
        for entry in solutions:
            file.write(",".join(str(e) for e in entry) + "\n")

    def end(self):
        self.resultFile.close()

    def saveModel(self):
        torch.save(self.agent.model.state_dict(), self.generateFilename("models", "model"))
