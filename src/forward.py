#!/usr/bin/python

class ForwardError:
    def __init__(self, message):
        self.message = message

class Forward:
    def __init__(self, params):
        #   Init the instance vars
        self.ports = None
        self.protocols = []
        self.interfaces = None
        self.destination = "127.0.0.1"
        self.destport = None
        self.description = None

        #   Check protocols
        if params["protocols"] and not params["protocols"] == "*":
            protocols = [x.strip() for x in params["protocols"].split(",")]
            for p in protocols:
                if p in ("tcp", "udp"):
                    self.protocols.append(p)
                else:
                    raise ForwardError("Unrecognised protocol: %s" % p)
        else:
            self.protocols = ["tcp", "udp"]

        #   Check ports
        if not params["ports"]:
            raise ForwardError("You must define some ports to forward")
        elif not params["ports"] == "*":
            self.ports = params["ports"]

        #   Interfaces
        if params["interfaces"] and not params["interfaces"] == "*":
            self.interfaces = [x.strip() for x in params["interfaces"].split(',')]
        #   Destination
        if params["destination"]:
            self.destination = params["destination"]
        #   Destport
        if params["destport"]:
            self.destport = params["destport"]
        #   Description
        if params["description"]:
            self.description = params["description"]

        #   Some validation
        if self.destination == "127.0.0.1" and not self.destport:
            raise ForwardError("No change of destination - pointless forward!")

    def getrule(self):
        output = []

        if self.description:
            output.append("# " + self.description)

        if self.interfaces:
            for i in self.interfaces:
                for p in self.protocols:
                    preroute = "${IPTABLES} -t nat -A PREROUTING -p %s --dport %s -j DNAT --to %s" \
                            % (p, self.ports, self.destination)
                    if self.destport:
                        preroute += ":" + self.destport
                    forward = "${IPTABLES} -A FORWARD -p %s --dport %s -j ACCEPT" \
                            % (p, self.ports)
                    output.append(preroute)
                    output.append(forward)
        else:
            for p in self.protocols:
                preroute = "${IPTABLES} -t nat -A PREROUTING -p %s --dport %s -j DNAT --to %s" \
                        % (p, self.ports, self.destination)
                if self.destport:
                    preroute += ":" + self.destport
                forward = "${IPTABLES} -A FORWARD -p %s --dport %s -j ACCEPT" \
                        % (p, self.ports)
                output.append(preroute)
                output.append(forward)

        output.append('')

        return output
