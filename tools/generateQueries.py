import os
import sys
from util import joinHelper as jh
from util import databases

database = databases.ErgastF1
jh.setTableData(database.tables, database.relations)

# read first file
if len(sys.argv) > 2:
    nJoins = int(sys.argv[1])
    folder = "data/" + sys.argv[2]
else:
    print("Requires 2 arguments: number of relations, folder in data/")
    print("A third option is optional and can be 'nC' if queries without COUNT should be generated")
    exit()

if len(sys.argv) > 3 and sys.argv[3] == "nC":
    selectCount = False
else:
    selectCount = True
    print("Pass nC as third option to use SELECT * instead of SELECT COUNT(*)")

useAliases = False

# folder to store generated queries
os.mkdir(folder)

# generate joins
joins = jh.generatePossibleJoins(database.tables, database.relations, nJoins)


def generateQuery(tables, db: databases.ErgastF1):
    if selectCount:
        sql = "SELECT Count(*) FROM \n"
    else:
        sql = "SELECT * FROM \n"
    ta = []
    for index, table in enumerate(tables):
        if useAliases:
            ta.append(table + " AS " + db.aliasT(db, table))
        else:
            ta.append(table)
    sql += ",\n ".join(ta)
    sql += "\nWHERE \n"
    cond = []
    for a in tables:
        for b in tables:
            if a != b and (a, b) in db.relations:
                if useAliases:
                    cond.append(db.relationsAlias[(db.aliasT(db, a), db.aliasT(db, b))])
                else:
                    cond.append(db.relations[(a, b)])
    sql += "\nAND ".join(cond)
    sql += ";"
    return sql, len(cond) > len(tables) - 1


for i, tset in enumerate(joins[nJoins]):
    sql, special = generateQuery(tset, database)
    if not special:
        file = open(folder + "/" + str(i) + ".sql", "w")
    else:
        file = open(folder + "/" + str(i) + "_special.sql", "w")

    file.write(sql)
    file.close()
