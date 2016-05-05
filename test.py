from ctypes import *
import json


#test_dll = cdll.LoadLibrary('./test.so')
#cpu_dll = cdll.LoadLibrary('./libvmi/examples/so-cpu-usage.so')
cpu_dll = cdll.LoadLibrary('./out-of-box-api.so')

class ProcInfo(Structure):
    pass

ProcInfo._fields_ = [
    ("type", c_int),                    # type of the process: new, exist, ended
    ("state", c_long),                   # task_struct->state
    ("pid", c_int),                     # vmi_pid_t == int  | task_struct->pid
    ("name", c_char_p),                 # pointer for process name
    ("priority", c_uint),               # task_struct->rt_priority
    ("cpu_percent", c_double),          # calculated cpu usage percentage
    ("physical_memory_usage", c_int64), # the total amount of physical memory used by the task
    ("virtual_memory_usage", c_int32),  # virtual size of a process
    ("memory_percent", c_double),       # calculated memory usage percentage
    ("next", POINTER(ProcInfo)),        # pointer to next process_info struct
    ("r_utime", c_int64), # the total amount of physical memory used by the task
    ("r_stime", c_int64), # the total amount of physical memory used by the task
    ("r_virt", c_int32), # the total amount of physical memory used by the task
    ("r_rss", c_int64) # the total amount of physical memory used by the task
]

class ImageOffsets(Structure):
    pass

ImageOffsets._fields_ = [
    ("rt_priority_offset", c_uint64),
    ("state_offset", c_uint64),
    ("tasks_offset", c_uint64),
    ("name_offset", c_uint64),
    ("pid_offset", c_uint64),
    ("mm_offset", c_uint64),
    ("total_vm_offset", c_uint64),
    ("rss_stat_offset", c_uint64),
    ("element_offset", c_uint64),
    ("utime_offset", c_uint64),
    ("stime_offset", c_uint64)
]

def _ImageOffsets_set_parameters(self, **kwargs):                                  
    # Set parameters in ImageOffsets._fields_                                      
    try:
        for field in self._fields_:                                                
            key = field[0]
            if isinstance(kwargs[key], int):
                self._fields_[key] = kwargs[key]
            elif (isinstance(kwargs[key], str) and                                 
                  kwargs[key].startswith('0x')):
                self.__setattr__(key, int(kwargs[key], 0))                         
    
    except KeyError, e:
        # Necessary keys should be provided in kwargs
        raise KeyError('"' + str(e) + '" should be provided')                      
   
ImageOffsets.set_parameters = _ImageOffsets_set_parameters

#test_dll.test_main.restype = POINTER(ProcInfo)
cpu_dll.process_list.argstype = (c_char_p, POINTER(ImageOffsets))
cpu_dll.process_list.restype = POINTER(ProcInfo)

NULL_PTR = POINTER(c_int)()


img_offsets = ImageOffsets()
kwargs = {'element_offset': '0x8', 'pid_offset': '0x2ac', 'rt_priority_offset': '0x5c', 'tasks_offset': '0x238', 'mm_offset': '0x270', 'stime_offset': '0x410', 'total_vm_offset': '0xa8', 'state_offset': '0x0', 'rss_stat_offset': '0x2a8', 'utime_offset': '0x388', 'name_offset': '0x460'}
img_offsets.set_parameters(**kwargs)

print "img_offsets.tasks_offset = " + str(img_offsets.tasks_offset)


test_result = cpu_dll.process_list("instance-00000239", byref(img_offsets))
head = test_result


results = []

while 1:
    contents = test_result.contents
    results.append(contents)
    test_result = contents.next
    if not test_result:
        break

print len(results)
print [(result.name, result.physical_memory_usage, result.cpu_percent, result.memory_percent) for result in results]


cpu_dll.free_process_info_list.argtypes = [POINTER(ProcInfo)]
cpu_dll.free_process_info_list(head)
