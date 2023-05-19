import time
import ast
import numpy as np
from datetime import datetime
import torch
from termcolor import colored
from ML import interpretation

import statistics as stat
from jooServer import JooServer

# Local import
from postgresqlJoins import PostgresqlJoins

from util import databases
from util import joinHelper as jh

from datetime import datetime
from ML.models import vqc

from util.databases import ErgastF1
from util.dataformat import DataFormat


class QmlServer(JooServer):

    prefix = "qml"

    def __init__(self, model, crossFilter) -> None:
        super().__init__()
        self.crossFilter = crossFilter
        self.model = model

    def choose(self, tables, cardinalities, logData):
        tablesSorted = sorted(tables)
        features = [database.toId(e) for e in tablesSorted]
        joinOrders = jh.generateJoinOrders(tablesSorted)
        if self.crossFilter == "pre":
            joinOrders = list(filter(lambda e: not jh.isCrossJoin(e), joinOrders))

        with torch.no_grad():
            featureTensor = torch.tensor(features)
            prediction = self.model(featureTensor)
            selected = inter.select(prediction, len(joinOrders))

        if self.crossFilter == "post":
            selections = torch.topk(prediction, 15)
            selected = choice.item()
            for choice in selections.indices[0]:
                if not jh.isCrossJoin(joinOrders[selected]):
                    break
                else:
                    print(colored("Cross join choosen:", 'red'), selected)

        order = joinOrders[selected]

        return order


if __name__ == "__main__":
    print("Running QML server")

    crossFilter = "none"  # valid are: none, pre, post

    # setting database for feature mapping and cross join elimnation
    database = databases.ErgastF1()
    jh.setTableData(database.tables, database.relations)

    # filename for trained model and settings
    trainedFile = 'Loss_New_simple_rx_False_20_yz_circular_cx_linear_8000_SGD_[0.01, 100, 0.9]_Loss_New_42_False_1_ModuloMax'

    # read settings from file
    with open("results/settings/" + trainedFile + ".conf") as file:
        settings = ast.literal_eval(file.read())

    print(settings)

    #env = PostgresqlJoins(ErgastF1(), inputFile="ergastf1nC.csv", dataFormat=DataFormat(0,1,-1))
    env = PostgresqlJoins(ErgastF1(), inputFile="ergastf1nCnoCross.csv", dataFormat=DataFormat(0, 1, -1))

    # create model
    model = vqc(settings=settings, num_inputs=env.getInputSize(), num_outputs=env.getOutputSize())
    # load weights
    model.load_state_dict(torch.load("results/models/" + trainedFile + ".model"))

    inter: interpretation.Interpretation = interpretation.fromString(settings["loss"], model)

    # show model quality
    print(env.elvaluateModel(inter))

    server = QmlServer(inter, crossFilter)
    server.run()
