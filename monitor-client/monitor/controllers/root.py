import copy
import datetime
import json
import yaml

from pecan import expose, redirect, request
from webob.exc import status_map
from monitor.controllers.v1 import root as v1
       
class RootController(object):
    v1 = v1.V1Controller()
 
    @expose(generic=True, template='json')
    def index(self, instance_name=None):
        #TODO(pwwp):
        # Add capabilities support.
        return {}


    @index.when(method='POST', template='json')
    def index_post(self, instance_name):
        # Load image offsets and instance name from request
        image_offsets = None
        kwargs = yaml.safe_load(request.body)
        print kwargs

        try:
            image_offsets = ImageOffsets()
            image_offsets.set_parameters(**kwargs)
        except KeyError, e:
            return self.error_json('KeyError', e)
        except ValueError, e:
            # Errors detected when converting hex string to int
            return self.error_json('ValueError', e)

        proc_controller = VMProcessList(instance_name, image_offsets)
        return proc_controller.get_process_list()


    @expose('error.html')
    def error(self, status):
        try:
            status = int(status)
        except ValueError: 
            status = 500
        message = getattr(status_map.get(status), 'explanation', '')
        return dict(status=status, message=message)

    def error_json(self, error_type, error_msg):
        return {'status': 'error', 
                'error_msg': str(error_msg)}
