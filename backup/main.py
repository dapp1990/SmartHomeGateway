from mininet.net import Mininet
from mininet.node import RemoteController
from mnt.topology import gatewayNet
from mininet.log import setLogLevel, info

from statistics_module.basic_engine import StatisticsEngine

test = StatisticsEngine()

test.save_statistics("frvfrv")