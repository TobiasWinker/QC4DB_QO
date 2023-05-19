# source environment variables from top level of the git repository
source $(git rev-parse --show-toplevel)/source.sh

if (( $(id -u) == 0 )); then
    echo "Please do not run as root"
    exit
fi

if [ ! -n "$QC4DB_QO_BASE" ] 
then
    echo "Env variable QC4DB_QO_BASE not set. Forgot to include source.sh?"
    exit
fi;

if [ ! -d "$QC4DB_QO_BASE" ]; then
    mkdir $QC4DB_QO_BASE
fi

# The following to libraries may be missing
# sudo apt install libreadline-dev
# sudo apt install zlib1g-dev

if [ ! -d "$QC4DB_QO_BASE/postgresql" ]; then
    echo "Installing postgresql"
    cd $QC4DB_QO_BASE
    mkdir postgresql
    cd postgresql
    wget https://ftp.postgresql.org/pub/source/v14.4/postgresql-14.4.tar.gz
    tar xvfz postgresql-14.4.tar.gz
    cd postgresql-14.4
    mkdir install
    mkdir database
    ./configure --prefix=$QC4DB_QO_BASE/postgresql/install --enable-debug
    make -j $(nproc)
    make install
    cd ..
    cd ..
fi
initdb -D $PSQL_DATA_DIRECTORY


