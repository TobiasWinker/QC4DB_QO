# path to the root of the git repository
rep_base=$(git rev-parse --show-toplevel)

if [ ! -n "$rep_base" ] 
then
    echo "Repository base not found. This script has to be run inside the qc4db repository"
    exit
fi;

source $rep_base/source.sh

plugin_location="$QC4DB_QO_REP/postgresql_plugin"
plugin_name="qc4db_joo"

if (( $(id -u) == 0 )); then
    echo "Please do not run as root"
    exit
fi

# $QC4DB_QO_BASE is the root of the data directory


if [ ! -n "$QC4DB_QO_BASE" ] 
then
    echo "Env variable QC4DB_QO_BASE not set. Forgot to include source.sh?"
    exit
fi;

plugin_source="$rep_base/$plugin_location"

if [ ! -n "$plugin_source" ] 
then
    echo "Plugin folder not found. This script has to be run inside the qc4db repository"
    exit
fi;


echo "Repository: "
echo $rep_base
echo "Data directory"
echo $QC4DB_QO_BASE

# copy plugin code
cp -r $plugin_source/$plugin_name $PSQL_SRC_DIRECTORY/contrib/

# backup config if the plugin is not yet installed
if ! grep -q "qc4db" "$PSQL_DATA_DIRECTORY/postgresql.conf"; then
  cp $PSQL_DATA_DIRECTORY/postgresql.conf $PSQL_DATA_DIRECTORY/postgresql.conf.backup
fi

# copy config to enable plugin 
cp $plugin_source/postgresql.conf $PSQL_DATA_DIRECTORY/

# build and install plugin
cd $PSQL_SRC_DIRECTORY/contrib/$plugin_name
make  -j $(nproc)
make install

