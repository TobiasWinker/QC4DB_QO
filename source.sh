
export QC4DB_QO_REP_BASE=$(git rev-parse --show-toplevel)
export QC4DB_QO_BASE=$QC4DB_QO_REP_BASE

# PostgreSQL
export PATH=$QC4DB_QO_BASE/postgresql/install/bin:$PATH
export LD_LIBRARY_PATH=$QC4DB_QO_BASE/postgresql/install/lib/:$LD_LIBRARY_PATH
export PSQL_DATA_DIRECTORY=$QC4DB_QO_BASE/postgresql/database
export PSQL_SRC_DIRECTORY="$QC4DB_QO_BASE/postgresql/postgresql-14.4"
