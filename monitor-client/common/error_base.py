

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


class InstanceDoesNotExist(ClientSideError):
    def __init__(self, instance_name):
        msg = instance_name + ' does not exist'
        super(InstanceDoesNotExist, self).__init__(404, msg)

