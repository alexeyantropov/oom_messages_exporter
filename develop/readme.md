# Disclaimer
Originally I use MacOS for developing and write all scripts for Mac. Ispite of this there isn't any reason for not working on Linux systems but could get some difficulties on Windows.

# VS Code and miniconda intergration

## Mac OS

### Install the miniconda distro if it's needed 
```
# curl -o /tmp/m.sh -s https://repo.anaconda.com/miniconda/Miniconda3-py39_23.5.2-0-MacOSX-$(uname -m).sh && bash /tmp/m.sh -b -p $HOME/miniconda
```

### Prepare a separate env
Create 
```
$ ~/miniconda/bin/conda env create -f ./develop/miniconda-environment.yml
```

Update
```
$ ~/miniconda/bin/conda env update -f ./develop/miniconda-environment.yml
```

Check
```
$ ~/miniconda/envs/oom_messages_exporter/bin/pip list local | egrep 'prom'
```

## vs code config
A workspace configuration into ./.vscode/settings.json. It contains the path for the miniconda env for syntax and methods highlighting.

## Pip install test a built release
```
$ ~/miniconda/bin/conda env create -f ./develop/miniconda-environment-pypi-test.yml
$ ~/miniconda/envs/oom_messages_exporter_test/bin/python3 -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ oom-messages-exporter
$ ~/miniconda/envs/oom_messages_exporter_test/bin/python3 ~/miniconda/envs/oom_messages_exporter_test/lib/python3.9/site-packages/oom_messages_exporter.py
$ ~/miniconda/bin/conda env remove -n oom_messages_exporter_test
```

# How to run 

## tests
```
$ ./tests/run.sh
```
## example
Send Ctrl+C after the end of presentaion.
```
$ ./examples/exporter-containerd.sh
```
```
$ ./examples/exporter-systemd.sh
```


# How to build
You need a config file based on the root dir with name ./.pypirc.ini with your pypi tokens:
```
[testpypi]
  username = __token__
  password = pypi-...
[pypi]
  username = __token__
  password = pypi-...
```

## Upload to test pypi
Next run the following script:
```
$ ./develop/upload-test.sh
```

## Upload to pypi
```
$ ./develop/upload-prod.sh
```

## Build a docker container
```
$ ./develop/docker-build.sh
```
