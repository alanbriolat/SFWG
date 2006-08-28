#!/usr/bin/python

import re

class Forward:
    
    ports = None
    protocols = None
    destination = None
    destport = None
    description = None

    def __init__(self, params, desc):
        port, proto, dest, dport = params
        self.description = desc
    
        # Check the validity of the port definition
        if not port:
            raise "You must define some ports to open!"
        else:
            self.ports = port
        """
            try:
                start, finish = port.split(':')
            except ValueError:
                start = finish = port

            if 0 < int(start) < 65536 and 0 < int(finish) < 65536:
                if int(finish) < int(start):
                    raise "End port higher than start port"
                else:
                    self.ports = start, finish
            else:
                raise "Port number out of range"
        """

        # Check which protocols are being allowed
        if not proto:
            self.protocols = "tcp", "udp"
        else:
            protocols = []
            for p in proto.split(','):
                p = p.strip().lower()
                if p in ("tcp", "udp"):
                    protocols.append(p)
            if len(protocols) == 0:
                raise "No valid protocols were defined - use 'tcp', 'udp' or 'tcp,udp', or \
                        leave the field blank (will use both tcp and udp by default)"
            else:
                self.protocols = set(protocols)

        if not re.match("^[0-9]{1,3}(\.[0-9]{1,3}){3,3}$", dest):
            raise "Destination must be an IP address - later versions will support hostnames"
        else:
            self.destination = dest

        if not dport:
            self.destport = None
        else:
            self.destport = dport
        
    def getrule(self, wan_interfaces):
        output = []

        if self.description:
            output.append("# " + self.description)

        ports = self.ports

        for p in self.protocols:
            for i in wan_interfaces:
                preroute = \
                        "iptables -t nat -A PREROUTING -i %s -p %s --dport %s -j DNAT --to %s" \
                        % (i, p, ports, self.destination)
                if self.destport:
                    preroute += ":%s" % (self.destport)
                forward = \
                        "iptables -A FORWARD -i %s -p %s --dport %s -j ACCEPT" \
                        % (i, p, ports)
                output.append(preroute)
                output.append(forward)
        output.append('')

        return output
