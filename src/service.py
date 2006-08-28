#!/usr/bin/python

class Service:

    ports = None
    protocols = None
    description = None

    def __init__(self, params, desc):
        # Split up parameters - these are the result of split('|') on a config
        # line usually
        port, proto = params
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

    def getrule(self):
        output = []
        
        if self.description:
            output.append("# " + self.description)

        ports = self.ports

        for p in self.protocols:
            output.append("iptables -A INPUT -p %s --dport %s -j ACCEPT" % (p, ports))
        output.append('')

        return output
