from math import log, pi
import random
import numpy as np

from torch import Tensor
import torch
from ML.interpretation import Interpretation

from util import databases
from util import dataformat


class PostgresqlJoins():
    """
    Class representing a benchmark of joins
    """

    settings = {
        "features": "simple",
        "reward": "rational",
    }

    # csv format
    dataFormat: dataformat.DataFormat

    def __init__(self, database: databases.Database, inputFile="", settings={}, dataFormat: dataformat.DataFormat = dataformat.DEFAULT_FORMAT):
        self.settings.update(settings)
        self.data = []
        self.database = database
        self.dataFormat = dataFormat
        self.nJoinOrders = 0
        self.current_query = 0
        self.rewardType = self.settings["reward"]
        self.featureType = self.settings["features"]
        self.__evaluationSet = None
        self.setMaxId(self.database.maxId())
        if inputFile != "":
            # load data
            with open("data/" + inputFile, "r") as input:
                self.load_data(input)

    def step(self):
        # select new random query
        self.current_query = random.randrange(0, len(self.data))
        datapoint = self.data[self.current_query]
        observation = datapoint["features"]
        rewards = self.rewards(datapoint)
        return observation, rewards

    # returns initial state
    def reset(self) -> list[float]:
        """Start/Restart by selecting a random query and returning it"""
        self.current_query = random.randrange(0, len(self.data))
        return self.data[self.current_query]["features"]

    def load_data(self, file):
        id = 0
        for entry in file:
            tmp = entry.split(",")
            if self.dataFormat.n > -1:
                nJoinOrders = min(len(tmp) - self.dataFormat.first, self.dataFormat.n)
            else:
                nJoinOrders = len(tmp) - self.dataFormat.first
            self.nJoinOrders = max(nJoinOrders, self.nJoinOrders)
            features = []
            values = []
            query = tmp[self.dataFormat.query].split(";")
            # extract features
            for t in query:
                features.append(self.database.toId(t))

            # extract values and find best and worst
            min_id = -1
            min_value = 2147483647
            max_id = -1
            max_value = 0
            # iterate over the values
            for i in range(0, nJoinOrders):
                value = float(tmp[self.dataFormat.first + i])
                values.append(value)
                if value < 0:
                    continue
                #find best value
                if value < min_value:
                    min_value = value
                    min_id = i
                if value > max_value:
                    max_value = value
                    max_id = i
            datapoint = {
                "id": id,
                "features_raw": features,
                "features": self.feature_map(features),
                "values": values,
                "best_value": min_value,
                "best_id": min_id,
                "worst_value": max_value,
                "worst_id": max_id,
            }
            self.data.append(datapoint)
            id += 1

    def checkData(self):
        for entry in self.data:
            print("Num values: ", len(entry["values"]))

    def evaluate(self, action):
        datapoint = self.data[self.current_query]
        rewards = self.rewards(datapoint)
        return rewards

    def evaluate(self, state, action):
        for entry in self.data:
            diff = abs(sum(state - entry["features"]))
            if diff < 0.01:
                return entry["values"][action]
        print(state, " not found")

    def test(self, id, action):
        datapoint = self.data[id]
        reward = self.calculateReward(datapoint, action)
        print("Id: ", id)
        print("Reward: ", reward)
        print("Best: ", datapoint["best_value"], ", Worst: ", datapoint["worst_value"], ", Choosen:", datapoint["values"][action])
        print("Counts: ", datapoint["values"])

    def elvaluateModel(self, model: Interpretation, evaluationSet=None):
        if evaluationSet is None:
            evaluationSet = self.data
        with torch.no_grad():
            sumLinear = 0
            sumLog = 0
            sumRational = 0
            countBest = 0
            countWorst = 0
            countWrong = 0
            countCross = 0
            # Multi thread evaluation
            tensor = torch.zeros(0, self.getInputSize())
            for entry in evaluationSet:
                tensor = torch.cat((tensor, torch.reshape(torch.tensor(entry["features"]), [1, self.getInputSize()])), 0)
            with torch.no_grad():
                predictions = model.model(tensor)
            for i, prediction in enumerate(predictions):
                entry = evaluationSet[i]
                selected = model.select(prediction, len(entry["values"]))
                if entry["values"][selected] == entry["best_value"]:
                    countBest += 1
                if entry["values"][selected] == entry["worst_value"]:
                    countWorst += 1
                if entry["values"][selected] == -1:
                    countCross += 1
                sumLinear += self.linearReward(entry, selected)
                sumLog += self.logReward(entry, selected)
                sumRational += self.rationalReward(entry, selected)

        count = len(evaluationSet)
        return [sumLinear / count, sumLog / count, sumRational / count, countBest, countWorst, countWrong, countCross]

    def listSolutions(self, model):
        result = []
        with torch.no_grad():
            for index, entry in enumerate(self.data):
                state = entry["features"]
                prediction = model(Tensor(state))
                selected = prediction.argmax().numpy() % len(entry["values"])
                reward = self.calculateReward(entry, selected)
                result.append([index, selected, reward])
        return result

    def newEvaluationSet(self, size=20):
        self.__evaluationSet = random.sample(self.data, size)

# --------------------------------- Getter / Setter -------------------------------------------

    def getInputSize(self):
        return len(self.data[0]["features"])

    def getOutputSize(self):
        return self.nJoinOrders

    def getEvaluationSet(self):
        if self.__evaluationSet is None:
            self.newEvaluationSet()
        return self.__evaluationSet

    def setRewardType(self, type):
        self.rewardType = type

    def setFeatureType(self, type):
        self.featureType = type

    def setMaxId(self, id):
        self.maxId = id
        self.shuffleArray = list(range(id + 1))
        random.shuffle(self.shuffleArray)

    def findEntryIdFeatures(self, ids):
        idSet = set(ids)
        for entry in self.data:
            if set(entry["features_raw"]) == idSet:
                return entry
        raise ValueError("No entry found for " + str(ids))

# ----------------------- Feature mapping -----------------------

    def feature_map(self, features: list[int]) -> list[float]:
        """
        Turns a list of ids into values suitable for angle encoding

        Maps the values in `features` from the interval
            [0,n]
        to the interval 
            [0,pi]

        Optionally extends/modifies the features      
        """
        if self.featureType == "double":
            return self.featureMapDouble(features)
        elif self.featureType == "shuffle":
            return self.featureMapDoubleShuffle(features)
        else:
            return self.featureMapSimple(features)

    def normalize(self, value):
        maxvalue = self.maxId
        newmax = pi
        return value * newmax / maxvalue

    def featureMapSimple(self, features):
        result = []
        for f in features:
            result.append(self.normalize(f))
        return result

    def featureMapDouble(self, features):
        result = []
        for f in features:
            result.append(self.normalize(f))
        for f in features:
            result.append(self.normalize(f))
        return result

    def featureMapDoubleShuffle(self, features):
        result = []
        for f in features:
            result.append(self.normalize(f))
        for f in features:
            result.append(self.normalize(self.shuffleArray[f]))
        return result


# ------------------------ Rewards -----------------------------

    def rewardsId(self, id: int):
        """Calculated all rewards for query with id `id`"""
        return self.rewards(self.data[id])

    def rewards(self, datapoint: list[float]):
        """Calculate rewards for the values `datapoint`"""
        rewards = []
        for i in range(0, len(datapoint["values"])):
            rewards.append(self.calculateReward(datapoint, i))
        return rewards

    def calculateReward(self, datapoint, action):
        if action == 15:
            return 0
        # check if join is invalid (cross or timeout)
        elif datapoint["values"][action] < 0:
            return 0
        # avoid division by zero
        elif datapoint["values"][action] == 0:
            return 1
        # choose reward type
        elif self.rewardType == "linear":
            return self.linearReward(datapoint, action)
        elif self.rewardType == "log":
            return self.logReward(datapoint, action)
        else:
            return self.rationalReward(datapoint, action)

    def linearReward(self, datapoint, action):
        if datapoint["values"][action] < 0:
            return 0
        elif datapoint["values"][action] == 0:
            return 1
        selected = datapoint["values"][action]
        best = datapoint["best_value"]
        worst = datapoint["worst_value"]
        if worst == best:
            return 1
        return 1.0 - (selected - best) / (worst - best)

    def rationalReward(self, datapoint, action):
        if datapoint["values"][action] < 0:
            return 0
        elif datapoint["values"][action] == 0:
            return 1
        selected = datapoint["values"][action]
        best = datapoint["best_value"]
        worst = datapoint["worst_value"]
        return best / selected

    def logReward(self, datapoint, action):
        if datapoint["values"][action] < 0:
            return 0
        elif datapoint["values"][action] == 0:
            return 1
        selected = log(datapoint["values"][action], 10)
        best = log(datapoint["best_value"], 10)
        worst = log(datapoint["worst_value"], 10)
        if worst == best:
            return 1
        return 1.0 - (selected - best) / (worst - best)
