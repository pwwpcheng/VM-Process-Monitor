import httplib
import json
import urllib2
import yaml

from common import error_base as err
from connections.connection_base import ConnectionBase

class MonitorClient(object):
    # client's address or ip
    addr = None
    
    # port running monitor api
    port = None
    
    # authentication related
    username = None
    password = None

    def __init__(self, addr, username=None, password=None, 
                 port=11235):
        self.addr = addr
        self.port = port
        self.username = username
        self.password = password
        

    def get_process_list(self, instance_name, image_name, image_offsets):
        # TODO(pwwp):
        # Add cache control for process list
        # Cache according to instance_name
        
        return self._get_process_list(instance_name, image_name, image_offsets)

    
    def _get_process_list(self, instance_name, image_name, image_offsets):
        # Fetch process list from client

        params = { 
            'server': self.addr,
            'port': self.port,
            'instance': instance_name,
            'image' : image_name,
            'version': 'v1'
            }
        url = 'http://%(server)s:%(port)s/%(version)s/'\
              'instances/%(instance)s/processes' % params
            
        headers  = {'Content-Type' : 'application/json'}

        _body = {
            'image_name': image_name,
            'image_offsets' : image_offsets.to_obj()
        }

        body = json.dumps(_body)

        req = ConnectionBase(url=url, headers=headers, 
                            body=body)
        #req = ConnectionBase(url=url, headers=headers)
        return req.get_data()
  

def get_hypervisor_authentication(hypervisor_name):
    #result = None
    #if hypervisor_name == 'computer242':
    result = {
        'addr': hypervisor_name,
        'username': None,
        'password': None,
        'port': 11235
    }
    #else:
    #    result = None
    return result
