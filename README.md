This is a demo of the idea of **DoppelgangerProxy**.

The *system structure* is :

tcp_client.py  <--> pt_forwarder.py <--> udp_server.py (NTP_server), 

where pt_forwarder.py works as a proxy and transforms the comunication between tcp_client.py and udp_server.py. The traffic in between mimics Network Time Protocol (NTP) in terms of syntax and timing.

The *usage* is:
- run 'python udp_server.py' in a terminal;
- run 'python pt_forwarder.py' in another terminal;
- run 'python tcp_client.py' in the third terminal.

Now you can see the communication between tcp_client and udp_server are transformed with wireshark sniffing.


