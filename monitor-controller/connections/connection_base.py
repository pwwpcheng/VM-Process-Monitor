import httplib
import json
import pdb
import urllib2
import yaml

from common import error_base as err

class ConnectionBase(object):
    url = None
    headers = None
    body = None
    request = None
    
    def __init__(self, url, headers=None, body=None):
        self.url = url
        self.headers = headers
        self.body = body

        self.request = urllib2.Request(url=self.url,
                                       headers=self.headers,
                                       data=self.body)

    def get_data(self):
        try:
            resp = urllib2.urlopen(self.request)
            return yaml.safe_load(resp.read())
        except urllib2.URLError as e:
            if e.getcode() == 404:
                raise err.AddressNotFound(self.url)
            raise err.ServerSideError(code=e.getcode(), msg=e.reason)
        #except TypeError, e:
        #    raise err.ServerSideError('Server returned nothing.')
        except httplib.BadStatusLine, e:
            raise err.ServerSideError('Error on preparing process list.' +
                                      ' Could be: instance_offset error')
    

