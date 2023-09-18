<!-- TOC -->

- [OOM Messages Exporter](#oom-messages-exporter)
- [Examples](#examples)
    - [OOM inside kubernetes containers](#oom-inside-kubernetes-containers)
    - [OOM on bare metal servers or VMs](#oom-on-bare-metal-servers-or-vms)
- [How to run](#how-to-run)
    - [Examples](#examples)
    - [Alerting rules](#alerting-rules)
    - [Production](#production)
    - [Config](#config)
- [Dependencies](#dependencies)

<!-- /TOC -->

# OOM Messages Exporter
An exporter for providing OOM Killer's kills in the Prometheus format. The exporter is compatible with containers runtimes and could be useful to investigate OOM Killer activity inside containers, servers or vms.

# Examples
The main metrics are 'oom_messages_exporter_last_killed_pid' and 'oom_messages_exporter_last_killed_time' those provide values of the last pid and the last time of killed processes since the exporter has started. You can configure Alertmanager on the ..._time metric  (value > now - last Xh) or on a change of the ..._pid metric by expression delta(_pid[xH]) != 0 function. Also you can combine both metric to get better alerts experience.

Provided labels are:
- command - a proc title of a killed process;
- namespace (opt, containers runtimes only)
- pod (opt, containers runtimes only)
- container (opt, containers runtimes only)

## OOM inside kubernetes containers
```
oom_messages_exporter_last_killed_pid{command="php-fpm: pool w",container="php-fpm",namespace="oldwebsite",pod="a-legacy-app"} 235362.0
oom_messages_exporter_last_killed_time{command="framework",container="nodejs",namespace="lovely-project",pod="awesome-backend"} 1.69484585513779e+09
```

## OOM on bare metal servers or VMs
For this case labels about containers runtime should be as 'None'
```
oom_messages_exporter_last_killed_pid{command="node /opt/www/p",container="None",namespace="None",pod="None"} 24190.0
oom_messages_exporter_last_killed_time{command="node /opt/www/p",container="None",namespace="None",pod="None"} 1.6948459852485702e+09
```

# How to run

## Examples
Collecting OOM Killer messages about processes in an operating system:
```
# ./examples/exporter-container.sh
```
Collecting OOM Killer messages inside containers:
```
# ./examples/exporter-systemd.sh
```
Output (exporter-container.sh):
```
$ curl -s http://localhost:9001/ | egrep -v '^#' | grep oom_messages_exporter_last_killed_
oom_messages_exporter_last_killed_pid{command="framework",container="nodejs",namespace="lovely-project",pod="awesome-backend"} 1.990532e+06
oom_messages_exporter_last_killed_pid{command="php-fpm: pool w",container="php-fpm",namespace="oldwebsite",pod="a-legacy-app"} 235362.0
oom_messages_exporter_last_killed_time{command="framework",container="nodejs",namespace="lovely-project",pod="awesome-backend"} 1.69484585513779e+09
oom_messages_exporter_last_killed_time{command="php-fpm: pool w",container="php-fpm",namespace="oldwebsite",pod="a-legacy-app"} 1.694845840949523e+09
```

## Alerting rules
**expr:**
```
time() - max_over_time(oom_messages_exporter_last_killed_time{container!="None"}[Xh]) < X*60*60
```
where: Xh - a time period in hours for looking the last OOM Killer kill.

**annotations.description:**
```
the last kill was in ns={{ $labels.namespace }}, pod={{ $labels.pod }}, ct={{ $labels.container }}, proc={{ $labels.command }}, {{ $value | humanizeDuration }} ago
```

## Production
```
# pip install oom_messages_exporter
# python3.9 oom_messages_exporter.py
```

## Config
All runtime configuration provides by environment variables:
- oom_messages_exporter_PORT - an exporter port (default: 9001)
- oom_messages_exporter_POLL_INTERVAL - log polling interval (default: 1 (sec))
- oom_messages_exporter_MESSAGES_LOG - a path to log (default: /var/log/messages)

# Dependencies
- python 3.9
- prometheus_client
