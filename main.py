from mininet.net import Mininet
from mininet.node import RemoteController
from mnt.topology import gatewayNet
from mininet.log import setLogLevel, info

from statistics_module.simple_statistics_manager import SimpleStatisticsManager

test = SimpleStatisticsManager()

test.save_statistics("frvfrv")