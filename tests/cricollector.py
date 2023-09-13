'''
A little convention about test names: test_(1)___(2), where:
1 - Name of a functionality or a method;
2 - A clarification or a detail describes the test.
'''

import sys

sys.path.append('./src')
import oom_messages_exporter

line_with_oom_pid = 3319125
line_with_oom_container_id = '2cc85334e5030168b240f87215d26ecb97dd99c09237bd0a03d8957dafb33187'
line_with_oom_template = 'Sep  3 10:00:05 some-kube-node1 kernel: [34268134.409242] oom-kill:constraint=CONSTRAINT_MEMCG,nodemask=(null),cpuset=2cc85334e5030168b240f87215d26ecb97dd99c09237bd0a03d8957dafb33187,mems_allowed=0,oom_memcg=/kubepods/burstable/pod62015ce8-a46f-4b0e-a5a1-3082235c62dd,task_memcg=/kubepods/burstable/pod62015ce8-a46f-4b0e-a5a1-3082235c62dd/{},task=framework,pid={},uid=5000'
line_with_oom = line_with_oom_template.format(line_with_oom_container_id, line_with_oom_pid)
line_with_oom_not_existen_container = line_with_oom_template.format('dummy', line_with_oom_pid)

cc = oom_messages_exporter.CriCollector()

def test_find_crictl___test_binary():
    assert cc.test_binary == './tests/crictl-mock.sh'
    assert cc.find_crictl(test_binary=True) == cc.test_binary

def test_find_crictl___test_patch():
    assert cc.find_crictl(test_path='./tests') == './tests/crictl'

def test_find_socket___test_socket():
    assert cc.test_socket == './tests/cri-test.sock'
    assert cc.find_socket(crictl='dummy', test_socket=True) == cc.test_socket

def test_find_socket___wo_crictl():
    assert cc.find_socket(crictl=None) is None

def test_find_socket___not_found():
    assert cc.find_socket(crictl='dummy') is None

def test_find_socket___test_dir():
    assert cc.find_socket(crictl='dummy', run_dir='./tests') == 'tests/containerd.sock'

def test_get_pid_from_oom_line___Ok():
    assert cc.get_pid_from_oom_line(line_with_oom) == line_with_oom_pid

def test_get_pid_from_oom_line___Fail():
    assert cc.get_pid_from_oom_line('blahblahblah') == -1

def test_get_containerID_from_oom_line___Well():
    assert cc.get_containerID_from_oom_line(line_with_oom) == line_with_oom_container_id

def test_get_containerID_from_oom_line___Fail():
    assert cc.get_containerID_from_oom_line('blahblahblah') is None

def test_add___no_crictl():
    cc_mocked = oom_messages_exporter.CriCollector()
    cc_mocked.crictl, cc_mocked.socket = None, cc_mocked.test_socket
    assert cc_mocked.add(line_with_oom) == -1

def test_add___no_socket():
    cc_mocked = oom_messages_exporter.CriCollector()
    cc_mocked.crictl, cc_mocked.socket = cc_mocked.test_binary, None
    assert cc_mocked.add(line_with_oom) == -1

def test_add___no_line():
    cc_mocked = oom_messages_exporter.CriCollector()
    cc_mocked.crictl, cc_mocked.socket = cc_mocked.test_binary, cc_mocked.test_socket
    assert cc_mocked.add('') == -1

def test_add___Wrong_Line():
    cc_mocked = oom_messages_exporter.CriCollector()
    cc_mocked.crictl, cc_mocked.socket = cc_mocked.test_binary, cc_mocked.test_socket
    assert cc_mocked.add('dummy') == -1

def test_add___crictl_mock_fail():
    cc_mocked = oom_messages_exporter.CriCollector()
    cc_mocked.crictl, cc_mocked.socket = cc_mocked.test_binary, cc_mocked.test_socket
    assert cc_mocked.add(line_with_oom_not_existen_container) == -1

def test_add___crictl_mock_no_json():
    cc_mocked = oom_messages_exporter.CriCollector()
    cc_mocked.crictl, cc_mocked.socket = './tests/crictl-mock_no_json.sh', cc_mocked.test_socket
    assert cc_mocked.add(line_with_oom) == -1

def test_add___crictl_mock_empty_json():
    cc_mocked = oom_messages_exporter.CriCollector()
    cc_mocked.crictl, cc_mocked.socket = './tests/crictl-mock_empty_json.sh', cc_mocked.test_socket
    assert cc_mocked.add(line_with_oom) == -1
    
def test_add___Well():
    cc_mocked = oom_messages_exporter.CriCollector()
    cc_mocked.crictl, cc_mocked.socket = cc_mocked.test_binary, cc_mocked.test_socket
    assert cc_mocked.add(line_with_oom) == line_with_oom_pid

def test_get___Well():
    cc_mocked = oom_messages_exporter.CriCollector()
    pid, name, data = 123, 'test', dict()
    data['container_name'] = name
    cc_mocked.crictl, cc_mocked.socket = cc_mocked.test_binary, cc_mocked.test_socket
    cc_mocked.collection[pid] = data
    assert cc_mocked.get(pid)['container_name'] == name

def test_get___Wrong():
    cc_mocked = oom_messages_exporter.CriCollector()
    assert cc_mocked.get(1234) is None