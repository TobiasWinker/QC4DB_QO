if [ ! -n "$QC4DB_QO_BASE" ] 
then
    echo "Env variable QC4DB_QO_BASE not set. Forgot to include source.sh?"
    exit
fi;

cp $PSQL_DATA_DIRECTORY/postgresql.conf.backup $PSQL_DATA_DIRECTORY/postgresql.conf 
