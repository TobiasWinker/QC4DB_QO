import argparse
from datetime import datetime
import psycopg2
from util import joinHelper as jh
from util import dataHelper as dh
import os
from util.databases import ErgastF1

import time

jh.setDatabase(ErgastF1())

start = time.time()

parser = argparse.ArgumentParser()
# Add arguments for command line with defaults
# The folder in data/ which contains the queries
parser.add_argument("-q", "--queries", default='queries_4nC_filtered')
parser.add_argument("-g", "--geqo", action="store_true")
parser.add_argument("-T", "--timeout", default=120000)

args = parser.parse_args()

# connect to database
conn = psycopg2.connect(database='ergastf1', host='127.0.0.1', port=5432)
conn.autocommit = True
cursor = conn.cursor()

cursor.execute('SET statement_timeout=' + str(args.timeout))

#cursor.execute('SET join_collapse_limit TO 1')

if args.geqo:
    cursor.execute('SET geqo_threshold TO 2')
    print("# Using GEQO")

print("#Timeout: " + str(args.timeout))
print("#Date: " + datetime.now().strftime("%d/%m/%Y, %H:%M"))

# assign directory
queries = 'queries_5nC'

# if test=True don't run Analyze, only test if the jooSever is working
test = False

# iterate over files in
# that directory
directory = "data/" + queries
print("# Queries =", directory)
countTimeouts = 0
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    # checking if it is a query file
    if f.endswith(".sql"):
        with open(f, 'r') as file:
            query = file.read()
            tables = dh.queryToTableList(queries, filename)
            tables.sort()
            joins = jh.generateJoinOrders(tables)
            for i in range(105):
                try:
                    isCrossJoin = jh.isCrossJoin(joins[i])
                    startExe = time.time()
                    if test or isCrossJoin:
                        cursor.execute("EXPLAIN  (FORMAT JSON)" + query)
                    else:
                        cursor.execute("EXPLAIN  (ANALYZE, FORMAT JSON)" + query)
                    result = cursor.fetchall()
                    endExe = time.time()
                    tree = jh.extractJoinTree(result)
                    duration = jh.extractTimeFromJSON(result) if not test else 0
                    durationTime = endExe - startExe
                    if isCrossJoin:
                        raise Exception()
                    print(f, ";", durationTime, ";", tree, ";", 0, ";", duration, ";", i)
                except Exception as e:
                    countTimeouts += 1
                    print(f, ";", args.timeout / 1000, ";", [], ";", 1, ";", args.timeout, ";", i)

end = time.time()
print("# Timeout:", args.timeout)
print("# Number timeouts", countTimeouts)
print("# Duration: " + str(end - start))

cursor.close()
conn.close()

exit()
