rep_base=$(git rev-parse --show-toplevel)

#!/bin/bash
createdb ergastf1
psql -d ergastf1 -a -f $rep_base/data/datasets/ergastf1/create.sql
psql -d ergastf1 -a -f $rep_base/data/datasets/ergastf1/load.sql
