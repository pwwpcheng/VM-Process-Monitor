#VM Process Monitor


VM Process is a light-weighted web service that can be used
to monitor cpu and memory usage of processes on virtual machines.
This project provides out-of-the-box non-intrusive monitoring
experience on virtual machines, which spares the need for users 
to install any monitor plug-ins into his vm instance. Techniques
behind this project is implemented through LibVMI APIs and 
linux headers reading.

## BEFORE RUNNING:

It is assumed that OpenStack Nova project is installed on 
this machine, and there are currently running instances. 
ProcessMonitor is implemented through LibVMI APIs, which needs 
libvirt support. Please ensure that libvirt is properly 
configured before installing libvmi. 
To check if libvirt is correctly configured, run the
following command:

**\# virsh list**

You should see a list of running instances on current hypervisor.
If not, then there could be something wrong with libvirt. Please
solve these issues first.


## INSTALLATION:

The project is written with C and Python 2.7. Please check if 
you have installed Python2.7 and GCC compiler. Also, some extra
python libraries are necessary for processing process information,
including, yet not limited to:

httplib, urllib2, yaml

You may install them through pip via *pip install <packet-name>*. 

Install pecan framework: 

http://www.pecanpy.org/ 


Install LibVMI:

http://libvmi.com/docs/gcode-install.html


Compile out-of-box monitor 

**\# gcc -fPIC out-of-box-api.c -lvmi ../libvmi/libvmi.h -shared -o out-of-box-api.so**


Configure config file located at:

./monitor-client/config.py
./monitor-controller/config.py


Configure pecan installation at both monitor client
and monitor controller folder:

**\# cd monitor-[client|controller]/**

**\# python setup.py develop**


## RUNNING:

Run pecan services from both monitor-controller and 
monitor-client.
 
**\# pecan serve config.py**


## ENLIGHTENED BY:

Non-intrusive, out-of-band and out-of-the-box systems monitoring in the cloud

Authors:	
Sahil Suneja	University of Toronto, Toronto, ON, Canada
Canturk Isci	IBM T.J. Watson Research Center, Yorktown Heights, NY, USA
Vasanth Bala	IBM T.J. Watson Research Center, Yorktown Heights, NY, USA

http://dl.acm.org/citation.cfm?id=2591971.2592009&coll=DL&dl=GUIDE
