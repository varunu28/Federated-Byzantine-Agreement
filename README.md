# Federated-Byzantine-Agreement-
Implementation of "Federated Byzantine Agreement" in Python

Implementation of FBA protocol with a quorum slice of 3 nodes.

#### How to run?
```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt

python fba_client.py 3000

python fba_server.py 3000
python fba_server.py 3001
python fba_server.py 3002
python fba_server.py 3003
```

The messages would be passed from client to the server on port 3000 from where it transmits to the nodes in the quorum. Once it gets the acceptance from a quorum slice, it sends message for confirmation to the quorum. Once it receives confirmations from the quorum slice, all the nodes in the slice would commit the transaction and the primary node would send a confirmation to the client.
