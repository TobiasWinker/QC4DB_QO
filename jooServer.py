import socket
import time
import traceback
import numpy as np
from datetime import datetime
import torch
from termcolor import colored

import statistics as stat

# Local import
from postgresqlJoins import PostgresqlJoins

from util import databases
from util import joinHelper as jh

from datetime import datetime


def printColor(s):
    print("\033[0;31m" + s + "\033[0m\n")


database = databases.ErgastF1()
jh.setTableData(database.tables, database.relations)

current_time = datetime.now().strftime("%H:%M:%S")
print("Start Time =", current_time)

# Fix seed for reproducibility
seed = 42
np.random.seed(seed)
torch.manual_seed(seed)


class JooServer:

    prefix = "template"

    HOST = '127.0.0.1'
    PORT = 17342

    nextOrder = 0

    def __init__(self) -> None:
        timestr = time.strftime("%m-%d_%H-%M-%S")
        self.joinLog = open("servers/" + self.prefix + "_" + timestr + ".log", 'w')

    def choose(self, tables, cardinalities, logData):
        orders = jh.generateJoinOrders(sorted(tables))
        result = orders[self.nextOrder]
        self.nextOrder += 1
        if self.nextOrder == 105:
            self.nextOrder = 0
        print("Next join order:", self.nextOrder)
        return result

    def onAccept(self, conn):
        logData = []
        # read data
        data = b'' + conn.recv(1024)
        splitpoint = data.index(0)  # seperator between tables and weights
        while splitpoint < 0:
            data = data + conn.recv(1024)
            splitpoint = data.index(0)
        # parse table names
        namesStr = data[:splitpoint].decode('utf-8')
        tables = namesStr.split(";")
        # read cardinalities
        data = data[splitpoint + 1:]
        number_of_relations = len(tables)
        expectedLen = 8 * ((1 << number_of_relations) - 1 - number_of_relations)
        # read until all data arrived
        while len(data) < expectedLen:
            data = data + conn.recv(1024)
        # parse cardinalities
        cardinalities = np.frombuffer(data, dtype=np.int64).tolist()
        print("Features:")
        print(tables, cardinalities)
        logData.append(tables)
        logData.append(cardinalities)

        order = self.choose(tables, cardinalities, logData)

        logString = ";".join(str(x) for x in logData)
        self.joinLog.write(logString)
        self.joinLog.write("\n")
        self.joinLog.flush()
        print("Log:", colored(logString, 'yellow'))
        print("Order choosen " + str(order))

        idString = jh.toIntString(order, tables)
        print(idString)
        conn.send(np.array(idString, dtype=np.int16).tobytes())

    def run(self):
        # open server socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.HOST, self.PORT))
            s.listen()
            print("Server started")
            try:
                while True:
                    print("Listening for connection")
                    # wait for connection
                    conn, addr = s.accept()
                    self.onAccept(conn)
            except Exception as e:
                print(e)
                traceback.print_exc()
                s.close()


if __name__ == "__main__":
    print("Running dummy server")
    server = JooServer()
    server.run()
