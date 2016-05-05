# Server Specific Configurations
server = {
    'port': '11235',
    'host': '0.0.0.0'
}

# Pecan Application Configurations
app = {
    'root': 'monitor.controllers.root.RootController',
    'modules': ['monitor'],
    'static_root': '%(confdir)s/public',
    'template_path': '%(confdir)s/monitor/templates',
    'debug': True,
    'errors': {
        404: '/error/404',
        '__force_dict__': True
    }
}

logging = {
    'root': {'level': 'INFO', 'handlers': ['console']},
    'loggers': {
        'monitor': {'level': 'DEBUG', 'handlers': ['console']},
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

# Absolute path for out-of-box-monitor.so 
# Example:
#   LIST_PROCESS_DLL_PATH = '/home/Ubuntu/VMProcessMonitor/monitor-client/out-of-box-monitor.so'
LIST_PROCESS_DLL_PATH = ''
