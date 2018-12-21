from __future__ import print_function
import sys
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import pickledb

from collections import defaultdict

PORT = int(sys.argv[1])

pickle_filename = "assignment3_" + str(PORT) + ".db"
db = pickledb.load(pickle_filename, False)
db.deldb()

CLIENT_PORT = 5000

ports = [3000, 3001, 3002, 3003]

class MulticastPingPong(DatagramProtocol):

    server_count = defaultdict(list)
    server_confirmation_count = defaultdict(list)

    is_primary = False

    def print_all_pickle_contents(self):
        print("*" * 25)
        for key in db.getall():
            print("{}: {}".format(key, db.get(key)))
        print("*" * 25)

    def update_pickle_file(self, key, value):
        if db.get(key):
            val = int(db.get(key))
            value += val
            db.set(key, value)
        
        db.set(key, value)
        print("Updated value of {} to ${}".format(key, value))
        db.dump()

    def startProtocol(self):
        """
        Called after protocol has started listening.
        """
        print("Joined Grouped")
        self.transport.joinGroup("228.0.0.5")
        print("Quoram slice of 3 nodes including self")

    def confirmation_checker_helper(self, datagram, address):
        timestamp = datagram.decode("UTF-8").split(":")[1]
        user = datagram.decode("UTF-8").split(":")[2].split("$")[0]
        amount = int(datagram.decode("UTF-8").split(":")[2].split("$")[1])

        if address[1] not in self.server_confirmation_count[timestamp]:
                if len(self.server_confirmation_count[timestamp]) < 2:
                    print("Received confirmation from {} for transaction {}:${}. Number of votes: {}".format(address[1], 
                                                                                                            user,
                                                                                                            amount, 
                                                                                                            len(self.server_confirmation_count[timestamp]) + 1))
                self.server_confirmation_count[timestamp].append(address[1]) 

        if len(self.server_confirmation_count[timestamp]) == 2:
            print("Transaction confirmed")
            print("Committing the transaction")
            self.update_pickle_file(user, amount)
            print("Updated transactions: ")
            self.print_all_pickle_contents()

            if self.is_primary:
                # Send response to client.
                print("Sending confirmation on Client {}".format(CLIENT_PORT))
                self.transport.write(b"Server: Pong", (address[0], 5000))

    def acceptance_checker_helper(self, datagram, address):
        user = datagram.decode('utf-8').split(":")[0]
        amount = int(datagram.decode('utf-8').split(":")[1][1:])
        timestamp = datagram.decode('utf-8').split(":")[2]
        port = int(datagram.decode('utf-8').split(":")[3])

        if address[1] == CLIENT_PORT:
            self.is_primary = True
        
        if timestamp not in self.server_count.keys() or len(self.server_count[timestamp]) < 2:
            print("Received a message for amount {} for user {} from {}".format(amount, 
                                                                                user , 
                                                                                "Client" if address[1] == CLIENT_PORT else address[1]))

        # Add a new port to server count if message exists
        if timestamp in self.server_count.keys():
            if address[1] not in self.server_count[timestamp]:
                self.server_count[timestamp].append(address[1])
                if len(self.server_count[timestamp]) <= 2:
                    print("Received confirmation from {}. Number of votes: {}".format(address[1], len(self.server_count[timestamp])))

        # Check for a new message
        if timestamp not in self.server_count.keys():
            self.server_count[timestamp] = []
            if address[1] != CLIENT_PORT:
                self.server_count[timestamp].append(address[1])
                print("Received confirmation from {}. Number of votes: {}".format(address[1], len(self.server_count[timestamp])))
            else:
                print("Received the transaction from client as a Primary Node ({})".format(port))
                print("Pre-prepare the transaction")

            # Send to peer nodes for acceptance
            for node in ports:
                if node != PORT:
                    data = user + ":$" + str(amount) + ":" + timestamp + ":" + str(PORT)
                    self.transport.write(data.encode('utf-8'), ("228.0.0.5", node))

        if timestamp in self.server_count.keys() and len(self.server_count[timestamp]) >= 2 and timestamp not in self.server_confirmation_count.keys():
            print("Transaction Accepted")
            print("Sending for confirmation of transaction")

            # Send to peer nodes for confirmation
            self.server_confirmation_count[timestamp] = []
            for node in ports:
                if node != PORT:
                    data = "CONFIRMATION" + ":" + timestamp + ":" + user + "$" + str(amount)
                    self.transport.write(data.encode('utf-8'), ("228.0.0.5", node))

    def datagramReceived(self, datagram, address):
        if len(datagram.decode('UTF-8').split(":")) == 3:
            self.confirmation_checker_helper(datagram, address)
        else:
            self.acceptance_checker_helper(datagram, address)
                

reactor.listenMulticast(PORT, MulticastPingPong(), listenMultiple=True)
reactor.run()