#!/bin/bash -x

check_file () {
    if ! test -f $1; then
        echo "The file $1 is not found!"
        exit 1
    fi
}

env_file='./develop/const.env'
check_file $env_file
source $env_file 
export $(eval "echo \"$(cat $env_file)\"")


basename=$(basename $0)

if test "$basename" = "upload-test.sh"; then
    repository='testpypi'
elif test "$basename" = "upload-prod.sh"; then
    repository='pypi'
else
    echo "Do not run upload.sh!"
    exit 1
fi

pypi_rc='./.pypirc.ini'
check_file $pypi_rc

find ./dist/ -delete
$PYTHON_EXE -m build && \
$PYTHON_EXE -m twine upload --verbose --config-file $pypi_rc --repository $repository dist/*
