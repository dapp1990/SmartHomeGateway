# sudo mn -- custom topology.py --topo


# sudo ovs-ofctl add-flow s2 in_port=1,actions=normal
# sudo ovs-ofctl add-flow s2 in_port=2,actions=1


# sudo ovs-vsctl set-controller s1 tcp:127.0.0.1

"""
Add new node in the topology

py net.addHost('h3')
py net.addLink(s2, net.get('h3'))
py s2.attach('s1-eth3')
py net.get('h3').cmd('ifconfig h3-eth0 10.0.10.3)
"""

from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
import time


def gatewayNet(num):
    "Simple topology"

    net = Mininet(controller=None)

    info('*** Adding controller\n')
    #net.addController('c0', controller=RemoteController, ip="127.0.0.1", port=6633)

    info('*** Add hosts and switches\n')

    server = net.addHost('h1', ip='10.0.10.1/24')
    serverswitch = net.addSwitch('s1')
    net.addLink(serverswitch, server)

    wlan0 = net.addSwitch('s2')
    net.addLink(serverswitch,wlan0)

    for i in range(num):
        iot = net.addHost("h{}".format(i+2), ip="10.0.10.{}/24".format(i+2))

        net.addLink(iot, wlan0)

    info('*** Starting network\n')
    net.start()

    info('*** Running CLI\n')
    CLI(net)



    info('*** Stopping network\n')
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    gatewayNet(3)

