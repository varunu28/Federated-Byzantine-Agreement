from __future__ import print_function
import time, sys, collections
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

message = ["foo:$10", "bar:$30", "foo:$20", "bar:$20", "foo:$30", "bar:$10"]

class MulticastPingClient(DatagramProtocol):

    idx = 0

    def startProtocol(self):
        self.transport.joinGroup("228.0.0.5")
        self.sendMessage()

    def datagramReceived(self, datagram, address):
        print("Datagram %s received from %s" % (repr(datagram), repr(address)))
        if self.idx != len(message):
            self.sendMessage()

    def sendMessage(self):
        data = message[self.idx] + ":" + str(time.time()) + ":" + str(5000)
        self.transport.write(data.encode('utf-8'), ("228.0.0.5", int(sys.argv[1])))
        self.idx = self.idx + 1

ports = [3000, 3001, 3002, 3003]

# for port in ports:
reactor.listenMulticast(5000, MulticastPingClient(), listenMultiple=True)
reactor.run()