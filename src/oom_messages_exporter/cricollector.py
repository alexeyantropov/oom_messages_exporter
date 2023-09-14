import json
import logging
import re
import subprocess
from pathlib import Path
from shutil import which
from typing import TypedDict

class ContainerLabels(TypedDict):
    container_name: str
    pod_name: str
    pod_namespace: str

class PodByPid(TypedDict):
    int: ContainerLabels

class CriCollector:

    """
    The CriCollector class needs the crictl binary.
    According an crictl output the class collects data about namespaces, pods and containers of killed by OOM Killer pids.
    NB: There isn't any Python CRI library :(

    I.e the class transforms a line like this:

    Sep  3 10:00:05 some-kube-node1 kernel: [34268134.409242] \
    oom-kill:constraint=CONSTRAINT_MEMCG,nodemask=(null),cpuset=2cc85334e5030168b240f87215d26ecb97dd99c09237bd0a03d8957dafb33187,\
    mems_allowed=0,oom_memcg=/kubepods/burstable/pod62015ce8-a46f-4b0e-a5a1-3082235c62dd,\
    task_memcg=/kubepods/burstable/pod62015ce8-a46f-4b0e-a5a1-3082235c62dd/2cc85334e5030168b240f87215d26ecb97dd99c09237bd0a03d8957dafb33187,\
    task=framework,pid=3319125,uid=5000

    to:

    -> task_memcg=/kubepods/burstable/poda8d92af7-9288-4612-9741-447b435a8157/4768664dd956fa2530931122cb16f4231368fb4809f7cbd5ca28d583f404517d
    -> 4768664dd956fa2530931122cb16f4231368fb4809f7cbd5ca28d583f404517d
    -> crictl --runtime-endpoint=unix://var/run/containerd/containerd.sock inspect 4768664dd956fa2530931122cb16f4231368fb4809f7cbd5ca28d583f404517d
    -> io.kubernetes.pod.namespace=..., io.kubernetes.pod.name=..., io.kubernetes.container.name=...
    -> {pid: {container_name: '...', pod_name: '...', 'pod_namespace': '...' }}

    """

    def __init__(self, *, test=False) -> None:

        """
        :param test: do not use in production, only for example!
        """

        self.test_binary = './tests/crictl-mock.sh'
        self.test_socket = './tests/cri-test.sock'
        self.collection = dict() # The collection of pids with exta data.
        self.crictl = self.find_crictl(test_binary=test)
        self.socket = self.find_socket(self.crictl, test_socket=test)

    def find_crictl(self, *, test_binary=False, test_path=None) -> str:

        """
        The methods looks for the crictl binary in $PATH and returns abs path to the binary.
        """

        if test_binary:
            logging.info('Using a test stub for crictl.')
            return(self.test_binary)
        
        tmp = which('crictl', path=test_path)  
        if tmp and len(tmp) > 0:
            logging.info('The crictl is found: "{}".'.format(tmp))
            return(tmp)

        logging.critical('An exe "crictl" is not found!')
        return(None)
    
    def find_socket(self, crictl: str, *, test_socket=False, run_dir='/var/run/containerd') -> str:

        """
        Looks for a container runtime socket by known socket names in given directory.  
        """

        if test_socket:
            logging.info('Using a test stub for runtime socket.')
            return(self.test_socket)
        
        if not crictl:
            logging.info('A path to crictl is not provided.')
            return(None)
        
        known_socks = ['dockershim.sock', 'containerd.sock', 'crio.sock']
        for sock in known_socks:
            p = Path('{}/{}'.format(run_dir, sock)) 
            if p.exists():
                logging.info('Runtine socket is found: "{}".'.format(str(p)))
                return(str(p))
        
        logging.critical('Runtime socket is not found!')
        return(None)
    
    def cri_inspect(self, id) -> ContainerLabels:

        """
        The crictl binary wrapper. Runs 'crctl inspect' with given container id.
        Returns a dict() with container name, pod and namespace.
        """

        cmd = [
            self.crictl,
            '--runtime-endpoint=unix:/{}'.format(self.socket),
            'inspect',
            id
        ]

        crictl_out = subprocess.run(cmd, capture_output=True, text=True)

        if len(crictl_out.stderr) > 0:
            return(ContainerLabels())

        try:
            crictl_out_json = json.loads(crictl_out.stdout)
        except:
            return(ContainerLabels())

        if 'status' in crictl_out_json and 'labels' in crictl_out_json['status']:
            ret = ContainerLabels()
            labels = crictl_out_json['status']['labels']

            if 'io.kubernetes.container.name' in labels:
                ret['container_name'] = labels['io.kubernetes.container.name']
            if 'io.kubernetes.pod.name' in labels:
                ret['pod_name'] = labels['io.kubernetes.pod.name']
            if 'io.kubernetes.pod.namespace' in labels:
                ret['pod_namespace'] = labels['io.kubernetes.pod.namespace']
            return(ret)
        
        # Nothing is found, return an empty data set.
        return(ContainerLabels())
    
    def get_pid_from_oom_line(self, line: str) -> int:

        """
        A simple method extracts pid from oom killer line from dmegs or messages log by given line.
        """

        regex = r'pid=(\d*),'
        tmp = re.search(regex, line, flags=re.IGNORECASE)
        if tmp and tmp.group(1).isdigit():
            logging.info('Got pid: "{}"'.format(tmp.group(1)))
            return(int(tmp.group(1)))
        
        return(-1)
    
    def get_containerID_from_oom_line(self, line: str) -> str:

        """
        A simple method extracts container id from oom killer line from dmegs or messages log by given line.
        """

        # ...,task_memcg=/kubepods/burstable/poda8d92af7-9288-4612-9741-447b435a8157/57953e6c546fa43d1ebadf04b16d4e324378ad03d704dadf2cd41a9481eae3f8,...
        regex = r'task_memcg=([\/a-zA-Z0-9\-]+)'
        tmp = re.search(regex, line, flags=re.IGNORECASE)

        if tmp and tmp.group(1):
            ct_id =  tmp.group(1).split('/')[-1]
            logging.info('Got ct id: "{}"'.format(ct_id))
            return(ct_id)
        
        return(None)
            
    def add(self, line: str) -> int:

        """
        The main method adds info about pid in the collection by given line with 'oom-kill' signature.
        """

        if not (self.crictl and self.socket):
            logging.critical('Vars self.crictl: "{}" or self.socket: "{}" are not set!'.format(self.crictl, self.socket))
            return(-1)
        if not line:
            return(-1)
        
        pid = self.get_pid_from_oom_line(line)
        container_id = self.get_containerID_from_oom_line(line)

        if pid < 0 or not container_id:
            return(-1)
        
        tmp = self.cri_inspect(container_id)
        if len(tmp) > 0:
            self.collection[pid] = tmp
            return(pid)
        
        return(-1)
    
    def get(self, pid: int) -> ContainerLabels:

        """
        The method returns extra info about a given pid from the collection.
        """

        if pid in self.collection:
            return(self.collection[pid])
        
        return(None)