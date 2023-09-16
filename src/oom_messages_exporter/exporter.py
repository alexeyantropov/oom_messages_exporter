import logging
import os
import time
import re

from .filetailer import FileTailer
from .cricollector import CriCollector

from prometheus_client import Gauge, start_http_server

class Exporter:

    """
    The class provides an exporter for collecting info about OOM Killer works from system logs.
    """

    def __init__(self, *, log: str, interval=1, test_enable='no'):

        """
        :param log: by default if's /var/log/messages.
        :param interval: the log pooling interval.
        :param test_enable: do not use it.
        """

        self.log = log
        self.interval = interval
        self.tailer = self.__tailer_setup()
        if self.tailer is None: # You can't init the class if log does not exist!
            raise FileNotFoundError(log)
        self.metrics_name_for_pid = 'oom_messages_exporter_last_killed_pid'
        self.metrics_name_for_time = 'oom_messages_exporter_last_killed_time'
        self.oom_sign_cgroup = 'Killed process'
        self.container_sign = '] oom-kill:'
        self.__metrics_setup()
        if test_enable.lower() == 'no':
            self.pid_collection = CriCollector()
        else:
            self.pid_collection = CriCollector(test=True)

    def __metrics_setup(self):

        """
        Initialization of prometheus metrics.
        """

        labels = ['command', 'namespace', 'pod', 'container']
        self.last_killed_pid = Gauge(self.metrics_name_for_pid,
            'The last pid killed by OOM killer',
            labels)
        self.last_killed_time = Gauge(self.metrics_name_for_time,
            'The last time when a pid is killed by OOM killer',
            labels)
        
    def __tailer_setup(self) -> FileTailer:

        """
        Initialization of the file tailer.
        """

        try:
            return(FileTailer(file=self.log))
        except Exception as err:
            logging.critical('Can not setup a tailer on the "{}" log!'.format(self.log))
            return(None)
        
    def __string_has_oom(self, line: str) -> bool:

        """
        Checks a given line and returns 'True' if the line seems like a message about OOM Killer. 
        """

        return(self.oom_sign_cgroup.lower() in line.lower())
    
    def __string_has_container(self, line: str) -> bool:

        """
        Checks a given line and returns 'True' if the line has an information about a container runtime.
        """
        
        return(self.container_sign.lower() in line.lower())
    
    def __extract_pid(self, line: str, sign: str) -> int:

        """
        Gets a pid from a given line if OOM has killed a process in the line.
        """

        regexp = r'{} (\d*)'.format(sign)
        m = re.search(regexp, line, flags=re.IGNORECASE)
        if m and m.group(1).isdigit():
            logging.info('Got pid: "{}"'.format(m.group(1)))
            return(int(m.group(1)))
        return(-1)
    
    def __extract_proc_name(self, line: str, sign: str) -> str:
        """
        Gets a process name from a given line if OOM has killed a process in the line.
        """
        regexp = r'{} \d* \((.*)\)\,?'.format(sign)
        m = re.search(regexp, line, flags=re.IGNORECASE)
        if m and m.group(1):
            logging.info('Got proc name: "{}"'.format(m.group(1)))
            return(m.group(1))
        return('Could not get a proc name from a line.')
    
    def __extract_cri_data(self, pid: int) -> list:

        """
        The method returns extra labels by a given pid if the killed pid was in a container.
        """

        pod_namespace, pod_name, container_name = None, None, None
        container_data = self.pid_collection.get(pid)
        if container_data:
            if 'pod_namespace' in container_data:
                pod_namespace = container_data['pod_namespace']
            if 'pod_name' in container_data:
                pod_name = container_data['pod_name']
            if 'container_name' in container_data:
                container_name = container_data['container_name']
        return([pod_namespace, pod_name, container_name])

    def __process_data(self, line: str) -> str:

        """
        The method processes each given line and tries to recognize needed data about OOM Killer.
        """
        
        # Data about container should saved into additional storage for future use.
        if self.__string_has_container(line):
            logging.info('Have got container data, transmit the data to pid collector')
            tmp = self.pid_collection.add(line)
            if tmp > 0:
                logging.info('Container is added for a pid: "{}"'.format(tmp))
                return('has container: is added')
            
            return('has container: is not added')

        # Counters would be incremented if OOM Killer killed a process.
        # Also the code below tries to add extra data about the killed process if the process worked in a container runtime.
        if self.__string_has_oom(line):
            logging.info('Got OOM Killer in a line')

            pid = self.__extract_pid(line, self.oom_sign_cgroup)
            labels = [self.__extract_proc_name(line, self.oom_sign_cgroup)] + self.__extract_cri_data(pid)
            self.last_killed_pid.labels(*labels).set(pid)
            self.last_killed_time.labels(*labels).set_to_current_time()

            return('has oom')

        # If nothing interesting were found the code would write a dummy string.
        n = 50
        logging.debug('Got string w/o OOM, the first {} symbols: "{}"'.format(n, line[0:n]))

        return('has not any')

    def run_metrics_loop(self, *, test_runs=-1, test_data='') -> bool:
        
        """
        The main endless loop. The loop calls tail() method from the file tailer and
        will process lines if the lines appear in the log.
        """

        i = 0
        while True:

            data = self.tailer.tail()

            # The following block only for testing!
            if test_runs > 0 and i > test_runs:
                break
            if test_runs > 0:
                i += 1
            if test_data: 
                data = test_data
            
            if len(data) > 0:
                logging.debug('Data occurred in log, amount of lines: "{}"'.format(len(data)))
            for line in data:
                self.__process_data(line)
                
            time.sleep(self.interval)

        return(True)
           
def main(): # pragma: no cover
    # Config
    test_enable = os.getenv('oom_messages_exporter_TEST', 'no')
    debug_enable = os.getenv('oom_messages_exporter_DEBUG', 'no')
    exporter_port = int(os.getenv('oom_messages_exporter_PORT', 9001))
    messages_log = os.getenv('oom_messages_exporter_MESSAGES_LOG', '/var/log/messages')
    poll_interval = int(os.getenv('oom_messages_exporter_POLL_INTERVAL', 1))
    
    # Set debug logging
    if debug_enable != 'no':
        logging.getLogger().setLevel(logging.DEBUG)
    logging.debug('debug is enable')

    # There is the metrics
    start_http_server(int(exporter_port))

    # The exporter setup
    ex = Exporter(log=messages_log, interval=poll_interval, test_enable=test_enable)
    logging.info('oom_messages_exporter started! port: {}.'.format(exporter_port))

    # Run it!
    ex.run_metrics_loop()
