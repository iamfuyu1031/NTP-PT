This is a demo of the idea of DoppelgangerProxy.

The system structure is :

tcp_client.py  <--> pt_forwarder.py <--> udp_server.py (NTP_server), 

where pt_forwarder.py works as a proxy and transforms the comunication between tcp_client.py and udp_server.py. The traffic in between mimics Network Time Protocol (NTP) in terms of syntax and timing.


