import datetime
import json
import subprocess
import re
import yaml

from common import error_base as err
from common.api_classes import ProcInfo, ImageOffsets
from ctypes import *
from pecan import conf, expose, redirect, request
from pecan.rest import RestController

class InstanceProcessController(object):
    '''Name of selected instance. e.g.: instance-00000001'''
    instance_name = ""

    '''Name of the image used by selected instance (Deprecated)'''
    image_name = ""
 
    '''Head pointer of process list struct'''
    process_list_ptr = None

    '''Linux header offsets of the image '''
    image_offsets = None

    '''process_list function pointer'''
    list_process = None

    '''Free dll allocated memory function pointer'''
    free_list_process = None

    '''Custom actions supported by pecan'''
    _custom_actions = {
        'processes': ['POST']
    }

    def __init__(self, instance_name):
        self.instance_name = instance_name
        
        list_process_dll = cdll.LoadLibrary(conf.LIST_PROCESS_DLL_PATH)
        self.list_process = list_process_dll.process_list
        self.free_list_process = list_process_dll.free_process_info_list

        self.free_list_process.argstype = (POINTER(ProcInfo))
        self.list_process.argstype = (c_char_p, POINTER(ImageOffsets))
        self.list_process.restype = POINTER(ProcInfo)

        
    def _prepare_process_list(self):
        # Prepare ProcInfo structure but not read it
        # Read this structure only when needed.
        # free outdated info to prevent memory leak
        if self.process_list_ptr is not None:
            self._free_resources()

        instance_name = create_string_buffer(self.instance_name)
        if self.image_offsets is None:
            self.process_list_ptr = self.list_process(instance_name, 
            C_NULL_PTR)   
        else:
            self.process_list_ptr = self.list_process(instance_name, 
                byref(self.image_offsets))
        
        # TODO(pwwp):
        # Disallow frequent calling on _prepare_process_list 
        # Try to construct result cache
        # self.last_fetched_time = datetime.datetime.now()    

    
    @expose(template='json')
    def processes(self):        
        # Read Procinfo structure and collect information
        # return json
        if request.method == 'POST':
            kwargs = yaml.safe_load(request.body)
            try:
                self.image_offsets = ImageOffsets(**kwargs)
            except KeyError, e:
                raise err.ClientSideError(e + ' must be provided')
            except ValueError, e:
                # Errors detected when converting hex string to int
                raise err.ClientSideError(e)

        process_info_list = []

        # store process
        self._prepare_process_list()

        list_ptr = self.process_list_ptr
        while True:
            if not list_ptr:
                break
            process_info_contents = list_ptr.contents
            process_info_list.append(process_info_contents)
            list_ptr = process_info_contents.next
        return process_info_list
    
    def _free_resources(self):
        self.free_list_process(self.process_list_ptr)
        self.process_list_ptr = None


class InstancesController(RestController):

    ''' List of instances located on this machine '''
    instances = []

    @expose()
    def _lookup(self, instance_name, *remainder):
        if instance_name in self.instances:
            return InstanceProcessController(instance_name), remainder
        else:
            raise err.InstanceDoesNotExist(instance_name)


    def __init__(self):
        proc1= subprocess.Popen(['virsh', 'list'],
                                stdout=subprocess.PIPE)
        proc2 = subprocess.Popen(['grep', 'running'],
                                stdin=proc1.stdout, stdout=subprocess.PIPE)
        proc1.stdout.close()
        proc2.stdout.close()
        instance_string_list = [ srv for srv in       
                                       proc2.communicate()[0].split('\n')]
        self.instances = [re.findall('([^ ]+)', instance)[1]
                       for instance in instance_string_list if len(instance) > 0]

    @expose('json')
    def get_all(self):
        return [ { 'instance_name': instance}
                    for instance in self.instances]
