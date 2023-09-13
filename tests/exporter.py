'''
A little convention about test names: test_(1)___(2), where:
1 - Name of a functionality or a method;
2 - A clarification or a detail describes the test.
'''

import sys
import os
import pytest

sys.path.append('./src')
import oom_messages_exporter

file_d_lines = os.getenv('file_d_lines')
non_existent_file = '/foo/bar/baz/txt'
string_with_oom_pid = 1234
string_with_oom_proc_name = 'node /opt/www/p'
string_with_oom = 'Memory cgroup out of memory: Kill process {} ({}) score 331 or sacrifice chil'.format(string_with_oom_pid, string_with_oom_proc_name)
string_with_oom = 'Sep  4 00:05:58 other-server kernel: [38469674.213429] Killed process {} ({}), UID 80, total-vm:1203112kB, anon-rss:329556kB, file-rss:15708kB, shmem-rss:0kB'.format(string_with_oom_pid, string_with_oom_proc_name)
string_wo_oom = 'just a line'

cri_line_with_oom_pid = string_with_oom_pid
cri_line_with_oom_container_id = '2cc85334e5030168b240f87215d26ecb97dd99c09237bd0a03d8957dafb33187'
cri_line_with_oom = 'Sep  3 10:00:05 some-kube-node1 kernel: [34268134.409242] oom-kill:constraint=CONSTRAINT_MEMCG,nodemask=(null),cpuset=2cc85334e5030168b240f87215d26ecb97dd99c09237bd0a03d8957dafb33187,mems_allowed=0,oom_memcg=/kubepods/burstable/pod62015ce8-a46f-4b0e-a5a1-3082235c62dd,task_memcg=/kubepods/burstable/pod62015ce8-a46f-4b0e-a5a1-3082235c62dd/{},task=framework,pid={},uid=5000'.format(cri_line_with_oom_container_id, cri_line_with_oom_pid)

def test_init___Fail_Not_exist():
    with pytest.raises(Exception):
        ex_ne = oom_messages_exporter.Exporter(log=non_existent_file)

ex = oom_messages_exporter.Exporter(log=file_d_lines)
ex.pid_collection.crictl = ex.pid_collection.test_binary
ex.pid_collection.socket = ex.pid_collection.test_socket

def test_init___Ok():
    assert ex is not None

def test_string_has_oom___is_True():
    assert ex._Exporter__string_has_oom(string_with_oom) == True

def test_string_has_oom___is_not_True():
    assert ex._Exporter__string_has_oom(string_wo_oom) == False

def test_extract_pid___Ok():
    oom_sign_cgroup = ex.oom_sign_cgroup
    assert ex._Exporter__extract_pid(string_with_oom, oom_sign_cgroup) == string_with_oom_pid

def test_extract_pid___Fail():
    oom_sign_cgroup = ex.oom_sign_cgroup
    assert ex._Exporter__extract_pid(string_wo_oom, oom_sign_cgroup) == -1

def test_extract_proc_name___Ok():
    oom_sign_cgroup = ex.oom_sign_cgroup
    assert ex._Exporter__extract_proc_name(string_with_oom, oom_sign_cgroup) == string_with_oom_proc_name

def test_extract_proc_name___Fail():
    oom_sign_cgroup = ex.oom_sign_cgroup
    assert ex._Exporter__extract_proc_name(string_wo_oom, oom_sign_cgroup) == 'Could not get a proc name from a string "just a line".'

def test_process_data___OOM_Sign_is_present():
    ex._Exporter__process_data(cri_line_with_oom)
    assert ex._Exporter__process_data(string_with_oom) == 'has oom'

def test_process_data___OOM_Sign_not_is_present():
    assert ex._Exporter__process_data(string_wo_oom) == 'has not any'

def test_process_data___Cri_data_is_present():
    assert ex._Exporter__process_data(cri_line_with_oom) == 'has container: is added'

def test_run_metrics_loop():
    assert ex.run_metrics_loop(test_runs=1, test_data=string_with_oom) == True
