import json
import urllib2
import yaml

from pecan import conf
from common import error_base as err
from connections.connection_base import ConnectionBase

class NovaConnection(object):
    # OpenStack server addresss (fetched from config file)
    openstack_server_addr = conf.openstack_server_addr

    # Port running nova-api
    nova_port = conf.nova_port

    # Nova version of OpenStack server(fetched from config file)
    nova_api_version = conf.nova_api_version

    # url for fetching server detail
    base_url = None

    # OpenStack Token
    token = None
    # Project ID or Tenant ID used for nova
    tenant_id = None

    base_url = None

    # detailed information for the requested instance
    data = None

    def __init__(self, token, tenant_id):
        self.token = token
        self.tenant_id = tenant_id
        self.base_url = 'http://%(server_addr)s:%(port)s/%(version)s/%(tenant_id)s/' % {
            'port': self.nova_port,
            'server_addr': self.openstack_server_addr, 
            'version' : self.nova_api_version,
            'tenant_id': self.tenant_id
            }
    
    def get_instance_image_id(self, instance_id):
        # Get the image name of a requested instance

        if self.data is None:
            self._get_instance_detail(instance_id)
        if self.data['id'] != instance_id:
            self._get_instance_detail(instance_id)

        try:
            return self.data['image']['id']
        except KeyError, e:
            return err.ServerSideError('instance_id "' + instance_id + '"'
                                       + ' does not have attribute image.id')

    def get_instance_name(self, instance_id):       
         # Get the name of a requested instance

        if self.data is None:
            self._get_instance_detail(instance_id)
        if self.data['id'] != instance_id:
            self._get_instance_detail(instance_id)

        try:
            return self.data['OS-EXT-SRV-ATTR:instance_name']
        except KeyError, e:
            return err.ServerSideError('instance_id "' + instance_id + '"'
                                       + ' does not have attribute' 
                                       + 'OS-EXT-SRV-ATTR:instance_name')

    def get_instance_hypervisor_name(self, instance_id):       
         # Get the name of a requested instance

        if self.data is None:
            self._get_instance_detail(instance_id)
        if self.data['id'] != instance_id:
            self._get_instance_detail(instance_id)

        try:
            return self.data['OS-EXT-SRV-ATTR:hypervisor_hostname']
        except KeyError, e:
            return err.ServerSideError('instance_id "' + instance_id + '"'
                                       + ' does not have attribute' 
                                       + 'OS-EXT-SRV-ATTR:hypervisor_hostname')


    def _get_instance_detail(self, instance_id):
        # Interact with Nova API through urllib2 conn
        # Store instance detailed info to self.data

        if self.token is None:
            raise err.ArgumentNotProvided('token')
        if self.tenant_id is None:
            raise err.ArgumentNotProvided('tenant_id') 


        url = self.base_url + 'servers/' + instance_id
        headers  = {'Content-Type' : 'application/json',
                    'X-Auth-Token': self.token }
        req = ConnectionBase(url, headers)
        
        self.data = req.get_data()['server']


