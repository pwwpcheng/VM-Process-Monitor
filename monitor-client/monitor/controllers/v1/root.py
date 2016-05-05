
from monitor.controllers.v1 import instances

class V1Controller(object):
    ''' Version 1 controller root '''
    instances = instances.InstancesController()
