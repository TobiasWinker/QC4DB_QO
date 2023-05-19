import argparse
import psycopg2
from util import joinHelper as jh
import os
from datetime import datetime
import time

start = time.time()

parser = argparse.ArgumentParser()

# Add arguments for command line with defaults
# The folder in data/ which contains the queries
parser.add_argument("-q", "--queries", default='queries_4nC_filtered')
parser.add_argument("-g", "--geqo", action="store_true")
# if test=True don't run Analyze, only test if the jooSever is working
parser.add_argument("-t", "--test", action="store_true")
parser.add_argument("-T", "--timeout", default=120000)

args = parser.parse_args()

# connect to database
conn = psycopg2.connect(database='ergastf1', host='127.0.0.1', port=5432)
conn.autocommit = True
cursor = conn.cursor()

cursor.execute('SET statement_timeout=' + str(args.timeout))

if args.geqo:
    cursor.execute('SET geqo_threshold TO 2')
    print("# Using GEQO")

print("#Timeout: " + str(args.timeout))
print("#Date: " + datetime.now().strftime("%d/%m/%Y, %H:%M"))

countTimeouts = 0
directory = "data/" + args.queries
print("# Queries =", directory)
# iterate over files in directory
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    # checking if it is a query file
    if f.endswith(".sql"):
        with open(f, 'r') as file:
            query = file.read()
            try:
                startExe = time.time()
                if args.test:
                    cursor.execute("EXPLAIN  (FORMAT JSON)" + query)
                else:
                    cursor.execute("EXPLAIN  (ANALYZE, FORMAT JSON)" + query)
                result = cursor.fetchall()
                endExe = time.time()
                tree = jh.extractJoinTree(result)
                duration = jh.extractTimeFromJSON(result) if not args.test else 0
                durationTime = endExe - startExe
                print(f, ";", durationTime, ";", tree, ";", 0, ";", duration)
            except Exception as e:
                #print(e)
                countTimeouts += 1
                print(f, ";", int(args.timeout) / 1000, ";", [], ";", 1, ";", args.timeout)

end = time.time()
print("# Timeout:", args.timeout)
print("# Number timeouts", countTimeouts)
print("# Duration: " + str(end - start))

cursor.close()
conn.close()

exit()
