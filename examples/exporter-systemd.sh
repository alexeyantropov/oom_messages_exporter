#!/bin/bash

env_file='./develop/.env'

if ! test -f $env_file; then
    echo "The env file ${env_file} is not found."
    exit 1
fi

source $env_file 
export $(eval "echo \"$(cat $env_file)\"")

export oom_messages_exporter_MESSAGES_LOG='/tmp/example_tailer_file.txt'

make_lines () {
    > $oom_messages_exporter_MESSAGES_LOG
    cat $messages_systemd_1 | while read line; do
        echo "$line" >> $oom_messages_exporter_MESSAGES_LOG
        sleep 0.01
    done
}

make_lines &

$PYTHON_EXE ./src/oom_messages_exporter.py
