from ctypes import *

class ProcInfo(Structure, object):
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

def _ProcInfo_to_json(self):
    if self.type == 0:
        return dict(
            type = "New Process",
            state =  0,
            pid = self.pid,
            name = self.name,
            priority = 0,
            cpu_usage = 0.0,
            #physical_memory_usage = "{.2}%".format(self.physical_memory_usage),
            physical_memory_usage = 0,
            virtual_memory_usage = 0,
            memory_percent = 0.0
        )
    elif self.type == 1:
        return dict(
            type = "Existed Process",
            state = self.state,
            pid = self.pid,
            name = self.name,
            priority = self.priority,
            cpu_usage = self.cpu_percent,
            #physical_memory_usage = "{.2}%".format(self.physical_memory_usage),
            physical_memory_usage = self.physical_memory_usage,
            virtual_memory_usage = self.virtual_memory_usage,
            memory_percent = self.memory_percent
        )        
    elif self.type == 2:
        return dict(
            type = "Ended Process",
            state =  0,
            pid = self.pid,
            name = self.name,
            priority = 0,
            cpu_usage = 0.0,
            #physical_memory_usage = "{.2}%".format(self.physical_memory_usage),
            physical_memory_usage = 0,
            virtual_memory_usage = 0,
            memory_percent = 0.0
        )

ProcInfo.__json__ = _ProcInfo_to_json

class ImageOffsets(Structure):
    pass

ImageOffsets._fields_ = [
    ("rt_priority_offset", c_ulong),
    ("state_offset", c_ulong),
    ("tasks_offset", c_ulong),
    ("name_offset", c_ulong),
    ("pid_offset", c_ulong),
    ("mm_offset", c_ulong),
    ("total_vm_offset", c_ulong),
    ("rss_stat_offset", c_ulong),
    ("element_offset", c_ulong),
    ("utime_offset", c_ulong),
    ("stime_offset", c_ulong)
]

def _ImageOffsets_set_parameters(self, **kwargs):
    # Set parameters in ImageOffsets._fields_ 
    try:
        for field in self._fields_:
            key = field[0]
            if isinstance(kwargs[key], int):
                self.__setattr__(key, kwargs[key])
            elif (isinstance(kwargs[key], str) and 
                  kwargs[key].startswith('0x')):
                self.__setattr__(key, int(kwargs[key], 0))
    
    except KeyError, e:
        # Necessary keys should be provided in kwargs
        raise KeyError('"' + str(e) + '" should be provided')
   
ImageOffsets.__init__ = _ImageOffsets_set_parameters

def getfields(classname):    
    return [field[0] 
            for field in classname._fields_]

def _ImageOffsets_to_object(self):
    obj = {}
    for field in getfields(ImageOffsets):
        # getattr returns ctypes.c_ulong
        # need to convert c_ulong to int before returning
        obj[field] = int(getattr(self, field))

    return obj

ImageOffsets.to_obj = _ImageOffsets_to_object

C_NULL_PTR = POINTER(c_int)()

