import json

from pecan import expose, redirect
from webob.exc import status_map

from common import error_base as err
from common.api_classes import ProcInfo, ImageOffsets
from connections.monitor_client import MonitorClient
from connections.monitor_client import get_hypervisor_authentication
from connections.glance_connection import GlanceConnection
from connections.nova_connection import NovaConnection

class RootController(object):
    @expose(generic=True, template='index.html')
    #@expose(generic=True, template='json')
    #def index(self, openstack_token, tenant_name, instance_id):
    def index(self):
        return {}

    @index.when(method='POST')
    def index_post(self, q):
        redirect('http://pecan.readthedocs.org/en/latest/search.html?q=%s' % q)

    @expose('json')
    def process_list(self, openstack_token, tenant_id, instance_id):
        # Get process list(json) for requested instance
        try:
            nova_conn = NovaConnection(openstack_token, tenant_id)
            image_id = nova_conn.get_instance_image_id(instance_id)
            hypervisor_name = nova_conn.get_instance_hypervisor_name(instance_id)
            instance_name = nova_conn.get_instance_name(instance_id)

            glance_conn = GlanceConnection(openstack_token, tenant_id, image_id)
            image_offsets = glance_conn.get_image_offsets()
            image_name = glance_conn.get_image_name()

        except (err.ClientSideError, err.ServerSideError), e:
            return self._error_json(e.err_msg)
       
        kwargs = get_hypervisor_authentication(hypervisor_name)
        client_conn = MonitorClient(**kwargs)

        try:
            proc_list = client_conn.get_process_list(instance_name, image_name,
                                                     image_offsets)
        except (err.ClientSideError, err.ServerSideError), e:
            return self._error_json(e.err_msg)

        return self._success_json(proc_list)


    @expose('error.html')
    def error(self, status):
        try:
            status = int(status)
        except ValueError:  # pragma: no cover
            status = 500
        message = getattr(status_map.get(status), 'explanation', '')
        return dict(status=status, message=message)

    def _error_json(self, err_msg):
        return {'status': 'error',
                'error_msg': str(err_msg)
               }


    def _success_json(self, data):
        return {'status': 'success',
                'data': data
               }
