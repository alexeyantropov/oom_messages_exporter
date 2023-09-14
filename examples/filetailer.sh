#!/bin/bash

env_file='./develop/const.env'

if ! test -f $env_file; then
    echo "The env file ${env_file} is not found."
    exit 1
fi

source $env_file 
export $(eval "echo \"$(cat $env_file)\"")
export example_tailer_file='/tmp/example_tailer_file.txt'

make_a_line () {
    echo -e "${i} $(echo "$(date)${i}"|md5)"
}

make_lines () {
    for i in {1..3}; do
        make_a_line
    done
    sleep 1

    for i in {4..8}; do
        make_a_line
    done
    sleep 2

    for i in {9..13}; do
        make_a_line
    done
    sleep 3
}

make_a_line > $example_tailer_file
make_lines > $example_tailer_file &

echo -e "You should see lines like this: '<NUM> <MD5 HASH>', you have to send Ctrl+C to stop the example script.\n"
$PYTHON_EXE ./examples/filetailer.py
