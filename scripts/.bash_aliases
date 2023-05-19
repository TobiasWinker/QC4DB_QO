alias sourcePG='source $(git rev-parse --show-toplevel)/source.sh'
alias startPG='sourcePG; pg_ctl start -D $PSQL_DATA_DIRECTORY'
alias stopPG='sourcePG; pg_ctl stop -D $PSQL_DATA_DIRECTORY'