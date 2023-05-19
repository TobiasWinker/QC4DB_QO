from typing import List
from util.databases import Database


def setTableData(tables: list, relations: dict):
    global _tables
    global _relations
    _tables = tables
    _relations = relations


def setDatabase(db: Database):
    setTableData(db.tables, db.relations)


def generatePossibleJoins(tables, relations, n=4):
    joins = {2: []}
    # 2 joins
    for key in relations.keys():
        joins[2].append(list(key))
    # n joins
    for nJoins in range(3, n + 1):
        joins[nJoins] = []
        for t in tables:
            for i, j in enumerate(joins[nJoins - 1]):
                if not t in j:
                    for r in joins[2]:
                        if (t == r[0] and r[1] in j) or (t == r[1] and r[0] in j):
                            newList = j.copy()
                            newList.append(t)
                            newList.sort()
                            if not newList in joins[nJoins]:
                                joins[nJoins].append(newList)
        joins[nJoins].sort()
    return joins


def toBitString(all: List, active):
    result = 0
    result |= 1 << all.index(active)
    return result


# query is a list of tables
def generateJoinOrders(query: List):
    '''
    Create a list with all possible join trees

    The list is created using dynamic programming
    Uses bit strings instead of sets to check for overlap between subtrees
    This should be significantly faster
    '''
    # dynamic programming
    n = len(query)
    level = [[] for _ in range(n + 1)]
    # level 1
    level[1].extend([(e, toBitString(query, e)) for e in query])
    # level 2 - n
    for new in range(2, n + 1):
        for i in range(1, (new // 2) + 1):
            for idL in range(len(level[i])):
                for idR in range(len(level[new - i])):
                    if (i == new - i) and (idR <= idL):
                        continue
                    left = level[i][idL]
                    right = level[new - i][idR]
                    if (left[1] & right[1]) == 0:
                        level[new].append(([left[0], right[0]], left[1] | right[1]))

    return [e[0] for e in level[n]]


def getRelation(a, b):
    for r in _relations:
        if (r[0] in a and r[1] in b) or (r[0] in b and r[1] in a):
            return r
    return None


def getAllRelations(tables: list) -> list:
    result = []
    for a in tables:
        for b in tables:
            if a != b and (a, b) in _relations:
                result.append(_relations[(a, b)])
    return result


def generateSQLJoin(query):
    """
    Generate the SQL string for the given join tree
    Arguments:
        query: the join order
    Returns:
        the SQL string representing the join
        a boolean telling if only inner joins are used
    """
    if not isinstance(query, list):
        return query, True, [query]
    else:
        sql1, inner1, tables1 = generateSQLJoin(query[0])
        sql2, inner2, tables2 = generateSQLJoin(query[1])
        condition = getRelation(tables1, tables2)
        result = "\n(" + sql1 + " JOIN " + sql2
        # check if a condition exists
        #if condition==None:
        #    print("No condition for "+str(tables1)+" and "+str(tables2))
        if not condition == None:
            result += "\n ON "
            result += _relations[condition]
        result += ")"
        tables = []
        tables.extend(tables1)
        tables.extend(tables2)
        return result, inner1 and inner2 and not condition == None, tables


def generateSQL(query, explain=True, analyze=True):
    join, inner, _ = generateSQLJoin(query)
    if explain:
        if analyze:
            sql = "EXPLAIN (ANALYZE, VERBOSE, FORMAT JSON) "
        else:
            sql = "EXPLAIN (VERBOSE, FORMAT JSON) "
    else:
        sql = ""
    sql += "SELECT * FROM \n " + join + ";"
    return sql, inner


def countIntermeditateResults(json):
    typ = json["Node Type"]
    ignore = ["Aggregate", "Gather", "Seq Scan", "Hash", "Index Only Scan", "Memoize", "Index Scan", "Sort", "Materialize"]
    join = ["Hash Join", "Merge Join", "Nested Loop"]
    if typ in join:
        # current node is a join node. Count its intermeditate rows
        intermediate = json["Actual Rows"]
    elif typ in ignore:
        # don't count this node
        intermediate = 0
    else:
        # unknown node
        print("Unknown Node type: " + typ)
    if "Plans" in json:
        # examine sub plans
        for p in json["Plans"]:
            intermediate += countIntermeditateResults(p)
    return intermediate


def extractJoinTree(json):
    if isinstance(json, list):
        if len(json) == 1:
            return extractJoinTree(json[0])
        else:
            return [extractJoinTree(child) for child in json]
    if isinstance(json, tuple):
        return extractJoinTree(json[0])
    if "Plan" in json:
        return extractJoinTree(json["Plan"])
    if "Plans" in json:
        return extractJoinTree(json["Plans"])
    return json["Relation Name"]


def extractTimeFromJSON(json):
    return json[0][0][0]["Plan"]["Actual Total Time"]


# compare two binary trees
# a call with not binary trees this will return False
# [] counts as a valid binary tree
def equalTrees(a, b):
    if type(a) != type(b): return False
    if isinstance(a, str): return a == b
    if (a == []) != (b == []): return False
    if (a == [] and b == []): return True
    if len(a) != 2 or len(b) != 2: return False
    return (equalTrees(a[0], b[0]) and equalTrees(a[1], b[1])) or (equalTrees(a[0], b[1]) and equalTrees(a[1], b[0]))


def flattenTree(tree):
    if isinstance(tree, list):
        lst = []
        for e in tree:
            lst.extend(flattenTree(e))
        return lst
    else:
        return [tree]


def isCrossJoin(tree):
    if tree == []: return False
    if not isinstance(tree, list): return False
    rela = flattenTree(tree[0])
    relb = flattenTree(tree[1])
    return isCrossJoin(tree[0]) or isCrossJoin(tree[1]) or getRelation(rela, relb) is None


def _toIntString(order, fs, nextId):
    res = []
    if isinstance(order[0], list):
        lstLeft, idLeft, nextId = _toIntString(order[0], fs, nextId)
        res.extend(lstLeft)
    else:
        idLeft = fs.index(order[0])
    if isinstance(order[1], list):
        lstRight, idRight, nextId = _toIntString(order[1], fs, nextId)
        res.extend(lstRight)
    else:
        idRight = fs.index(order[1])
    res.append(idLeft)
    res.append(idRight)
    print(idLeft, idRight, len(fs) - 1)
    return res, nextId, nextId + 1


def toIntString(order, fs):
    if order == []: return []
    result, _, _ = _toIntString(order, fs, len(fs))
    return result
