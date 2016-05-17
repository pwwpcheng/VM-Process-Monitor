import json

from pecan import conf
from common import error_base as err
from common.api_classes import ImageOffsets
from common.api_classes import getfields
from connections.connection_base import ConnectionBase

class GlanceConnection(object):
    # OpenStack server addresss (fetched from config file)
    openstack_server_addr = conf.openstack_server_addr

    # Port running glance-api
    glance_port = conf.glance_port

    # Glance version of OpenStack server(fetched from config file)
    glance_api_version = conf.glance_api_version

    # url for fetching server detail
    base_url = None

    # OpenStack Token
    token = None

    # Project ID or Tenant ID used for glance
    tenant_id = None

    # ID of requested image
    image_id = None

    # detailed information for the requested image
    data = None

    def __init__(self, token, tenant_id, image_id):
        self.token = token
        self.tenant_id = tenant_id
        self.image_id = image_id
        self.base_url = 'http://%(server_addr)s:%(port)s/%(version)s/' % {
            'port': self.glance_port,
            'server_addr': self.openstack_server_addr, 
            'version' : self.glance_api_version
            }
        self._get_image_detail()
        
    
    def get_image_name(self):       
         # Get the name of a requested image
        try:
            return self.data['name']
        except KeyError, e:
            return err.ServerSideError('image_id "' + image_id + '"'
                                       + ' does not have attribute' 
                                       + 'name')

    def get_image_offsets(self):
        # Get offsets list of requested image
        offset_name_list =  getfields(ImageOffsets)
        offsets = {}

        image_type = self._get_image_property('image_type', 'image')

        if image_type == 'snapshot':
            original_image_id = self._get_image_property('base_image_ref')
            original_image_conn = GlanceConnection(self.token, self.tenant_id,
                                                   original_image_id)
            return original_image_conn.get_image_offsets()

        for offset_name in offset_name_list:
            offsets[offset_name] = self._get_image_property(offset_name)
    
        return ImageOffsets(**offsets)


    def _get_image_detail(self):
        # Interact with Nova API through urllib2 conn
        # Store image detailed info to self.data

        url = self.base_url + 'images/' + self.image_id
        headers  = {'Content-Type' : 'application/json',
                    'X-Auth-Token': self.token }
        req = ConnectionBase(url=url, headers=headers)
        
        self.data = req.get_data()


    def _get_image_property(self, prop, default=None):
        if not self.data.has_key(prop):
            if default is not None:
                return default
            else:
                raise err.ImagePropertyNotExist(self.image_id, prop)
        return self.data[prop]
