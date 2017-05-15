from mininet.net import Mininet
from mininet.node import RemoteController
from mnt.topology import gatewayNet
from mininet.log import setLogLevel, info


setLogLevel('info')
gatewayNet()