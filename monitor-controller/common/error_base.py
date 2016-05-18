

class Error(Exception):
    err_code = None
    err_msg = None
    err_type = None
    err_diagnose = None

    def __init__(self, code, msg, diagnose=None):
        self.err_code  = code
        self.err_msg = msg
        self.err_diagnose = diagnose
        

class ClientSideError(Error):
    err_type = 'Client'

    def __init__(self, msg, code=400, diagnose=None):
        msg = 'Client Error: ' + str(msg)
        super(ClientSideError, self).__init__(code, msg, diagnose)


class ServerSideError(Error):
    err_type = 'Server'

    def __init__(self, msg, code=400, diagnose=None):
        msg = 'Server Error: ' + str(msg)
        super(ServerSideError, self).__init__(code, msg, diagnose)


class ArgumentNotProvided(ClientSideError):
    def __init__(self, arg_name):
        msg = '"' + str(arg_name) + '" not provided.'
        super(ArgumentNotProvided, self).__init__(msg)


class ImagePropertyNotExist(ClientSideError):
    def __init__(self, image_id, prop):
        param = {
            "image_id": image_id,
            "property": prop
        }
        msg = '"%(image_id)s" has no property "%(property)s". '\
              'Please run the following command in CLI:"'\
              ' glance image-update --property %(property)s='\
              '<value> %(image_id)s "' % params
        code = 404
        super(ImageHasNoProperties, self).__init__(code=code, msg=msg)


class ImageNotExist(ClientSideError):
    def __init__(self, image_id):
        msg = 'Requested image (id: %s ) does not exist.' % (image_id)
        code = 404
        super(ImageNotExist, self).__init__(code=code, msg=msg)


class AddressNotFound(ClientSideError):
    def __init__(self, url):
        msg = 'Requested address cannot be reached. Url: ' + url
        code = 404
        super(AddressNotFound, self).__init__(code=code, msg=msg)



