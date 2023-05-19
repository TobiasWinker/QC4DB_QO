from util import dataHelper as dh, databases
from util import joinHelper as jh

data = dh.loadBenchmark("4relations/allnC.txt")
jh.setDatabase(databases.ErgastF1())

nJoinorders = 15

for query, entries in data.items():
    relList = dh.queryToTableList("data/queries_4", query)
    values = [""] * nJoinorders
    for entry in entries:
        if not jh.isCrossJoin(entry["tree"]):
            values[entry["id"]] = str(entry["timePG"])
    lineList = [";".join(relList)]
    values = list(filter(lambda x: x != "", values))
    lineList.extend(values)
    print(",".join(lineList))
