import util.joinHelper as jh
import ast

# This file can be used to compare two benchmarks
# Each line in the benchmarks except comments (#) has the format:
# query ; time ; tree ; timeout ; timePostgreSQL
#   with
# query : filename of the query
# time : total execution time of the database call
# tree : join tree in python list notation
# timeout : 0 = no timeout , 1 = timeout
# timePostgreSQL : execution time of the query meassured by PostgreSQL EXPLAIN

bench = "4relations/dpnC.txt"
sourceFolder = ""
targetFolder = ""

ignoreSpecial = True

# set which key should be used for time calculations
tk = "time"  # total execution time meassured by python
#tk = "timePG"  # query execution time meassured by PostgreSQL


def loadBenchmark(filename):
    result = {}
    with open("benchmarks/" + filename, "r") as file:
        for line in file:
            if line[0] == "#": continue
            temp = line.split(";")
            if len(temp) < 4: continue
            query = temp[0].strip()
            if not query in result:
                result[query] = []
            result[query].append({"time": float(temp[1]), "tree": ast.literal_eval(temp[2].lstrip()), "timeout": temp[3].strip() == "1", "timePG": float(temp[4]), "raw": line})
    return result


data = loadBenchmark(bench)
for query in data:
    entry = data[query][0]
    queryname = query.split("/")[-1]
    if not entry["timeout"]:
        import shutil
        shutil.copy2('data/' + sourceFolder + '/' + queryname, 'data/' + targetFolder + '/')
    else:
        print(query)
