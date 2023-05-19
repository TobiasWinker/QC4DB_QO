import util.joinHelper as jh
import util.dataHelper as dh
import statistics as stat
import sys

# This file can be used to compare two benchmarks
# Each line in the benchmarks except comments (#) has the format:
# query ; time ; tree ; timeout ; timePostgreSQL
#   with
# query : filename of the query
# time : total execution time of the database call
# tree : join tree in python list notation
# timeout : 0 = no timeout , 1 = timeout
# timePostgreSQL : execution time of the query meassured by PostgreSQL EXPLAIN

# read args
# folder
if len(sys.argv) > 1:
    nRelations = sys.argv[1]
else:
    nRelations = input("Enter number of relations (is used as in folder name)")
if not nRelations.isdigit():
    print("First argument has to be an integer")
    exit()

# read first file
if len(sys.argv) > 2:
    bench1 = sys.argv[2]
else:
    bench1 = input("Enter name of first benchmark")

# second file
if len(sys.argv) > 3:
    bench2 = sys.argv[3]
else:
    bench2 = input("Enter name of second benchmark")

# ignore special queries
ignoreSpecial = False

delta = 0.0

# set which key should be used for time calculations
#tk = "time"     # total execution time meassured by python
tk = "timePG"  # query execution time meassured by PostgreSQL

data1 = dh.loadBenchmark(nRelations + "relations/" + bench1 + ".txt")
data2 = dh.loadBenchmark(nRelations + "relations/" + bench2 + ".txt")

print(len(data1), len(data2))

sum1 = 0
sum2 = 0
equal = 0
equalDiff = 0
better1 = 0
better1diff = 0
better1factor = []
better2 = 0
better2diff = 0
better2factor = []
rewards = []
for query in data1:
    if ignoreSpecial and "special" in query:
        continue
    if not query in data2:
        continue
    a = data1[query]
    b = data2[query]
    sum1 += a[tk]
    sum2 += b[tk]
    diff = a[tk] - b[tk]
    fraction = b[tk] / a[tk]
    rewards.append(fraction)
    #print(rewards[-1])
    if jh.equalTrees(a["tree"], b["tree"]) or abs(fraction - 1.0) < delta:
        equal += 1
        equalDiff += abs(diff)

    else:
        if a["timeout"] or b["timeout"]:
            print(a["tree"], "vs", b["tree"])
        if a[tk] < b[tk]:
            better1 += 1
            better1diff += abs(diff)
            better1factor.append(b[tk] / a[tk])
        else:
            if a[tk] / b[tk] > 100:
                print(query)
            better2 += 1
            better2diff += abs(diff)
            better2factor.append(a[tk] / b[tk])

# use max(..,1) to avoid division by 0
average1 = stat.mean(better1factor) if better1factor != [] else 1.0
average2 = stat.mean(better2factor) if better2factor != [] else 1.0

#print("Median 1 better:",stat.median(better1factor))
#print("Median 2 better:",stat.median(better2factor))

print("Equal join order {} times with Diff {:.3f}".format(equal, equalDiff))
print("{} is {:.3f}x better for {} queries with Diff {:.3f}".format(bench1, average1, better1, better1diff))
print("{} is {:.3f}x better for {} queries with Diff {:.3f}".format(bench2, average2, better2, better2diff))
if average2 != 0:
    print("{} quality compared to {}: {:.3f}".format(bench1, bench2, average1 / average2))

print("Time factor {:.3f}: {} with {} vs {} of {}".format(sum1 / sum2, bench1, sum1, sum2, bench2))
print("Average reward {}".format(stat.mean(rewards)))
print("Median reward {}".format(stat.median(rewards)))

if tk == "timePG":
    print("Using PostgreSQL time measurment. Values are in ms")
else:
    print("Using Python time meassurment. Times are in s")
