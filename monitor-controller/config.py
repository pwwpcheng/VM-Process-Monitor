# Server Specific Configurations
server = {
    'port': '11234',
    'host': '0.0.0.0'
}

# Pecan Application Configurations
app = {
    'root': 'monitorcontroller.controllers.root.RootController',
    'modules': ['monitorcontroller'],
    'static_root': '%(confdir)s/public',
    'template_path': '%(confdir)s/monitorcontroller/templates',
    'debug': True,
    'errors': {
        404: '/error/404',
        '__force_dict__': True
    }
}

logging = {
    'root': {'level': 'INFO', 'handlers': ['console']},
    'loggers': {
        'monitorcontroller': {'level': 'DEBUG', 'handlers': ['console']},
        'pecan.commands.serve': {'level': 'DEBUG', 'handlers': ['console']},
        'py.warnings': {'handlers': ['console']},
        '__force_dict__': True
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'color'
        }
    },
    'formatters': {
        'simple': {
            'format': ('%(asctime)s %(levelname)-5.5s [%(name)s]'
                       '[%(threadName)s] %(message)s')
        },
        'color': {
            '()': 'pecan.log.ColorFormatter',
            'format': ('%(asctime)s [%(padded_color_levelname)s] [%(name)s]'
                       '[%(threadName)s] %(message)s'),
        '__force_dict__': True
        }
    }
}

# Custom Configurations must be in Python dictionary format::
#
# foo = {'bar':'baz'}
#
# All configurations are accessible at::
# pecan.conf

openstack_server_addr = '166.111.143.220'
nova_port = 8774
nova_api_version = 'v2'

glance_port = 9292
glance_api_version = 'v2'

