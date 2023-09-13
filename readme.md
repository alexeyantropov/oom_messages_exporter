# OOM Messages Exporter
An exporter for providing OOM Killer in the Prometheus format. The exporter is compatible with containers runtimes and could be useful to investigate OOM Killer activity inside containers, servers or vms.

# Example data
The main metric is 'oom_messages_exporter_kills_total' that provides a counter of OOM kills since the exporter has started.

Providen labels are:
- pid - a pid of a killed process;
- command - a proc title of a killed process;
- namespace (opt, containers runtine only)
- pod (opt, containers runtine only)
- opt (opt, containers runtine only)
## OOM in kubernetes contaniers
```
oom_messages_exporter_kills_total{pid="3967383", command="node /opt/www/p",contanier="nodejs",namespace="lovely-project",pod="awesome-backend"} 1.0
oom_messages_exporter_kills_total{pid="1560850", command="node /opt/www/p",contanier="nodejs",namespace="lovely-project",pod="awesome-backend"} 1.0
```
## OOM in bare metal
For the case labels about contaniers runtine should be as 'None'
```
oom_messages_exporter_kills_total{command="python3.8",pid="3319125",contanier="None",namespace="None",pod="None"} 1.0
```
# How to run
## examples
Collecting OOM Killer messages about processes in an operating system:
```
# ./examples/exporter-containerd.sh
```
Collecting OOM Killer messages inside containers:
```
# ./examples/exporter-systemd.sh
```
Output:
```
$ curl -s http://localhost:9001/ | fgrep oom_messages_exporter_kills_total
# HELP oom_messages_exporter_kills_total The count of OOM operations, label "pid" has pid of a killed process, the label "command" is a proctitle of the killed process.
# TYPE oom_messages_exporter_kills_total counter
oom_messages_exporter_kills_total{command="framework",contanier="nodejs",namespace="lovely-project",pid="3967383",pod="awesome-backend"} 1.0
oom_messages_exporter_kills_total{command="framework",contanier="nodejs",namespace="lovely-project",pid="1560850",pod="awesome-backend"} 1.0
oom_messages_exporter_kills_total{command="framework",contanier="nodejs",namespace="lovely-project",pid="3319125",pod="awesome-backend"} 1.0
oom_messages_exporter_kills_total{command="framework",contanier="nodejs",namespace="lovely-project",pid="883095",pod="awesome-backend"} 1.0
oom_messages_exporter_kills_total{command="framework",contanier="nodejs",namespace="lovely-project",pid="3863600",pod="awesome-backend"} 1.0
```
## Production
```
# pip install oom_messages_exporter
# python3.7 oom_messages_exporter.py
```
## Config
All runtine conguration provides by environment variables:
- oom_messages_exporter_PORT - an exporter port (9001 by default)
- oom_messages_exporter_POLL_INTERVAL - log polling interval (1 (sec) by default)
- oom_messages_exporter_MESSAGES_LOG - a path to log (defult: /var/log/messages)
# Dependencies
- prometheus_client