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
file_zero_mode = os.getenv('file_zero_mode')
non_existent_file = '/foo/bar/baz/txt'
rotated_file = '/tmp/rotated.file'

ft = oom_messages_exporter.FileTailer(file=file_d_lines)

def recreate_a_dummy_file(f):
    if os.path.exists(f):
        os.remove(f)
    fd = open(f, 'w')
    fd.write('data\n')
    fd.close()

def add_strings_to_file(f, count):
    fd = open(f, 'a')
    for i in range(count):
        fd.write('data: {}\n'.format(i))
    fd.close()

def truncate_a_file(f):
    fd = open(f, 'a')
    fd.truncate(0)
    fd.close

def test_open___fail_1():
    with pytest.raises(Exception):
        ft_ne = oom_messages_exporter.FileTailer(file=non_existent_file)

def test_open___fail_2():
    with pytest.raises(Exception):
        oom_messages_exporter.FileTailer(file=file_zero_mode)

def test_open___well():
    assert ft._FileTailer__open_file() is True
    
def test_get_stat___fail():
    ft_gs = oom_messages_exporter.FileTailer(file=file_d_lines)
    ft_gs.file_name = non_existent_file
    assert ft_gs._FileTailer__get_stat() == {'inode': -1, 'size': -1}

def test_file_is_rotated___False():
    recreate_a_dummy_file(rotated_file)
    ft_rotated = oom_messages_exporter.FileTailer(file=rotated_file)
    add_strings_to_file(rotated_file, 2)
    assert ft_rotated._FileTailer__file_is_rotated() == False

def test_file_is_rotated___True():
    ft_rotated = oom_messages_exporter.FileTailer(file=rotated_file)
    recreate_a_dummy_file(rotated_file)
    assert ft_rotated._FileTailer__file_is_rotated() == True

def test_file_is_rotated___Truncated():
    recreate_a_dummy_file(rotated_file)
    add_strings_to_file(rotated_file, 2)
    ft_rotated = oom_messages_exporter.FileTailer(file=rotated_file)
    truncate_a_file(rotated_file)
    assert ft_rotated._FileTailer__file_is_rotated() == True

def test_tail___Ok_Simple():
    ft_tail = oom_messages_exporter.FileTailer(file=file_d_lines)
    assert len(ft_tail.tail()) == 0

def test_tail___Ok_NewLines():
    recreate_a_dummy_file(rotated_file)
    ft_tail = oom_messages_exporter.FileTailer(file=rotated_file)
    ft_tail.tail()
    how_to_add = [3, 33]
    for amount_of_lines in how_to_add:
        add_strings_to_file(rotated_file, amount_of_lines)
        assert len(ft_tail.tail()) == amount_of_lines

def test_tail___Ok_Rotated():
    recreate_a_dummy_file(rotated_file)
    add_strings_to_file(rotated_file, 2)
    ft_tail = oom_messages_exporter.FileTailer(file=rotated_file)
    ft_tail.tail()
    recreate_a_dummy_file(rotated_file)
    assert len(ft_tail.tail()) == 0

def test_tail___Deleted():
    recreate_a_dummy_file(rotated_file)
    ft_tail = oom_messages_exporter.FileTailer(file=rotated_file)
    ft_tail.tail()
    add_strings_to_file(rotated_file, 1)
    os.remove(rotated_file)
    assert len(ft_tail.tail()) == 1
    assert len(ft_tail.tail()) == 0
