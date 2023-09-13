#!/bin/bash

last_arg=${!#}
json="./tests/inspect-${last_arg}.json"

if test -f $json; then
    cat $json
    exit 1
else
    echo "FATA[0000] getting the status of the container \"${last_arg}\": rpc error: code = NotFound desc = an error occurred when try to find container \"${last_arg}\": not found" 1>&2
    exit 1
fi
