import re
import time
input_string = 'there is a OOM message Ifooph9rahy2uz6shaeveiX4Eiz6koongeex5cao4eRee3ootheit7ahdae1fahsh6choo0aij6aedoo8shuquidahbu5ohHaengadef6iej5Chesohv7heeWei6oosh6koghichookeeN4er5aat3ahQuiepei8peezieXikeehohThoo3Loof8aichauch2dohrooTieshohgh3Aeph2oos4quaiv1choe1Aish8wae1eegoh4tohquiegoo5X'
sub_string = 'oom'
n = 10000000

def with_lower(line):
    return(sub_string in line.lower())

def with_re(line):
    return(re.search(sub_string, line))

re_compiled = re.compile(sub_string)
def with_re_comlite(line):
    return(re_compiled.search(line))

# lower
lower_counter_start = time.perf_counter()
for i in range(n):
    with_lower(input_string)
lower_counter_end = time.perf_counter()

re_counter_start = time.perf_counter()
for i in range(n):
    with_re(input_string)
re_counter_stop = time.perf_counter()

re_com_counter_start = time.perf_counter()
for i in range(n):
    with_re_comlite(input_string)
re_com_counter_stop = time.perf_counter()

print('n: {}'.format(n))
print('Lower: {}'.format(lower_counter_end - lower_counter_start))
print('Re:    {}'.format(re_counter_stop - re_counter_start))
print('Re C:  {}'.format(re_com_counter_stop - re_com_counter_start))