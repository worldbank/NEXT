#!/usr/bin/env bash

# TEMORARY FIX TO MAKE AMI WORK
#HOST=$(curl http://169.254.169.254/latest/meta-data/public-ipv4)
HOST=$1
[[ -z "$1" ]] && HOST=localhost;  # by default HOST=localhost

export NEXT_BACKEND_GLOBAL_PORT=8000
export AWS_ACCESS_ID=None
export AWS_SECRET_ACCESS_KEY=None
export NEXT_FRONTEND_GLOBAL_PORT=8002
export NEXT_FRONTEND_GLOBAL_HOST=$HOST
export MASTER_LIST=$HOST
export AWS_BUCKET_NAME=next-database-backups
export ACTIVE_MASTER=$HOST
export SLAVE_LIST=
export NEXT_BACKEND_GLOBAL_HOST=$HOST
export FLASK_IP=$(ip -4 addr show docker0 | grep -Po 'inet \K[\d.]+') # gets docker0 ip

modify_ports=false
if [ "$modify_ports" = true ] ; then
    echo "Requesting sudo access to open some ports"
    sudo sysctl net.ipv4.tcp_tw_recycle=1
    sudo sysctl net.ipv4.tcp_tw_reuse=1
fi
    # this seems unnecessary for local, the reason it's commented out
    # it has something to do with docker which requires sudo access

    # this comes
	# http://www.speedguide.net/articles/linux-tweaking-121
	# from https://code.google.com/p/lusca-cache/issues/detail?id=89#c4
	# http://stackoverflow.com/questions/11190595/repeated-post-request-is-causing-error-socket-error-99-cannot-assign-reques

function abspath() {
    if [ -d "$1" ]; then
        echo "$(cd "$1"; pwd)"
    elif [ -f "$1" ]; then
        # file
        if [[ $1 == */* ]]; then
            echo "$(cd "${1%/*}"; pwd)/${1##*/}"
        else
            echo "$(pwd)/$1"
        fi
    fi
}

echo "Changing next_worker_startup.sh permissions..."
if [ "$#" -lt 2 ]; then
    dir=$(abspath ..);
    chmod +x ../next/broker/next_worker_startup.sh
    echo "No path to NEXT provided.  Assuming ../";
else
    dir=$(abspath $2);
    echo "ERROR: could not change permissions! Run 'chmod +x /path/to/.../next/broker/next_worker_startup.sh' yourself"
    echo "Using $1 as path to NEXT.";
fi

cp -f docker-compose.yml.pre docker-compose.yml
git_hash="$(git rev-parse HEAD)"
sed -i -e 's|{{NEXT_DIR}}|'"$dir"'|g' docker-compose.yml
sed -i -e 's|{{GIT_HASH}}|'"$git_hash"'|g' docker-compose.yml
sed -i -e 's|{{FLASK_IP}}|'"$FLASK_IP"'|g' docker-compose.yml

#echo "Stopping any existing vowpal wabbit containers"
#docker-compose -f ../next/vowpal_wabbit_image/vw-relevance.yaml stop
#docker-compose -f ../next/vowpal_wabbit_image/vw-product.yaml stop

#echo "Starting vowpal wabbit containers"
#docker-compose -f ../next/vowpal_wabbit_image/vw-relevance.yaml up -d --remove-orphans
#docker-compose -f ../next/vowpal_wabbit_image/vw-product.yaml up -d --remove-orphans
# note: should be a way to read any vw container modles in/pass as args

#echo "Stopping any existing machines..."
docker-compose stop
# note: is there a way to catch ctrl-c in this and dump vw container models to disk?

#echo "Starting a machine and all the dependeicies"
docker-compose up
