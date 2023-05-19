import ast


def loadBenchmark(filename):
    """
    Load a benchmark file into a list of dictionaries

    Each line in the benchmarks except comments (#) has the format:
    query ; time ; tree ; timeout ; timePostgreSQL
    with
    query : filename of the query
    time : total execution time of the database call
    tree : join tree in python list notation
    timeout : 0 = no timeout , 1 = timeout 
    timePostgreSQL : execution time of the query meassured by PostgreSQL EXPLAIN
    orderId: Id of this order in enumeration according to joinHelper.generateJoinOrders    
    """

    result = {}
    with open("benchmarks/" + filename, "r") as file:
        for line in file:
            # check if line is comment
            if line[0] == "#": continue
            # split into entries
            temp = line.split(";")
            # check if data format is correct
            if len(temp) < 5:
                raise ValueError("Invalid data format. 4 entries required in row but only {} found".format(len(temp)))
            # extract query name. Remove folder name and spaces
            query = temp[0].split("/")[-1].strip()
            if not query in result:
                result[query] = []
            result[query].append({"time": float(temp[1]), "tree": ast.literal_eval(temp[2].lstrip()), "timeout": temp[3] == "1", "timePG": float(temp[4]), "raw": line.rstrip()})
            if len(temp) >= 6:
                result[query][-1]["id"] = int(temp[5])
            # if only one entry found for query remove the list step
        for k, v in result.items():
            if len(v) == 1:
                result[k] = result[k][0]
    return result


def parseQuery(folder, file):
    filename = "data/{}/{}".format(folder, file)
    with open(filename, 'r') as f:
        query = f.read().replace('\r', ' ').replace('\n', ' ')
    # getting index of substrings
    idFrom = query.index("FROM")
    idWhere = query.index("WHERE")
    relString = query[idFrom + len("FROM") + 1:idWhere]
    rels = [x.strip() for x in relString.split(",")]
    filterString = query[idWhere + len("WHERE") + 1:-1]
    filters = [x.strip() for x in filterString.split("AND")]
    return rels, filters


def relsFromCondition(cond):
    temp = cond.split("=")
    return [temp[0].split(".")[0], temp[1].split(".")[0]]


def queryToTableList(folder, file):
    rels, _ = parseQuery(folder, file)
    return rels
