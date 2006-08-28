#!/usr/bin/python
__author__ = "Alan Briolat <alan@thev0id.net>"
__version__ = "0.1.1"

import getopt, sys, os, commands

from sfw import *
from configfile import *

# {{{ info functions

def showversion():
	print """sfwg - Simple FireWall Generator Version %s

This is free software.  You may redistribute copies of it under the terms of
the GNU General Public License <http://www.gnu.org/licenses/gpl.html>.
There is NO WARRANTY, to the extent permitted by law.

Created by %s""" % (__version__, __author__)


def showhelp():
	print """sfwg - Simple FireWall Generator Version %s

Usage: sfwg [OPTIONS] [CONFIGDIR...]

  -f, --forwards=FILE   Path to file containing port forwarding configuration
  -i, --icmp            Allow ICMP packets on WAN interfaces
  -I, --icmp-rate=COUNT Maximum rate to allow ICMP packets on WAN interfaces
                        (packets per second)
  -l, --lan=IF[,IF...]  All interfaces from which traffic is trusted
  -n, --nat             Use Network Address Translation - automatically enabled
                        if port forwarding is used
      --no-find         Do not check current directory and /etc/sfwg for 
                        services.conf and forwards.conf if not specified
  -o, --outfile=FILE    File to save the resulting script to
  -s, --services=FILE   Path to file containing configuration for ports on 
                        which connections should be accepted
  -w, --wan=IF[,IF...]  All interfaces from which traffic is untrusted
  -x, --execute         Do not output the script, instead execute it
  
      --help            Display this help
      --version         Display version information

This is free software.  You may redistribute copies of it under the terms of
the GNU General Public License <http://www.gnu.org/licenses/gpl.html>.
There is NO WARRANTY, to the extent permitted by law.

Created by %s""" % (__version__, __author__)

# }}}

if __name__ == "__main__":

    shortopts = "f:iI:l:no:s:w:x"
    longopts = ("forwards=", "icmp", "icmp-rate=", "lan=", "nat", "outfile=", \
            "no-find", "services=", "wan=", "execute", "help", "version")

    opts, args = getopt.getopt(sys.argv[1:], shortopts, longopts)

    if ("--help", "") in opts:
        showhelp()
    elif ("--version", "") in opts:
        showversion()
    else:

        # Set default options
        forwards = []
        services = []
        outfile = None
        findconfig = True
        execute = False

        # Create a new firewall object
        fw = SFW()

        for opt, val in opts:
            if opt in ("--forwards", "-f"):
                path = os.path.abspath(val)
                if os.path.isfile(path) and os.access(path, os.R_OK):
                    forwards.append(path)
            elif opt in ("--icmp", "-i"):
                fw.enable_icmp()
            elif opt in ("--icmp-rate", "-I"):
                fw.setopt("icmp_rate", val)
            elif opt in ("--lan", "-l"):
                fw.lan_interfaces(val)
            elif opt in ("--nat", "-n"):
                fw.enable_nat()
            elif opt in ("--no-find"):
                findconfig = False
            elif opt in ("--outfile", "-o"):
                outfile = os.path.abspath(val)
            elif opt in ("--services", "-s"):
                path = os.path.abspath(val)
                if os.path.isfile(path) and os.access(path, os.R_OK):
                    services.append(path)
            elif opt in ("--wan", "-w"):
                fw.wan_interfaces(val)
            elif opt in ("--execute", "-x"):
                execute = True

        # Add configs from config dirs
        if len(args) > 0:
            for arg in args:
                f = os.path.join(arg, 'forwards.conf')
                s = os.path.join(arg, 'services.conf')
                if os.path.isfile(f) and os.access(f, os.R_OK):
                    forwards.append(f)
                if os.path.isfile(s) and os.access(s, os.R_OK):
                    services.append(s)

        # Use /etc/sfwg/*.conf files if none specified
        if not forwards and not services and findconfig:
            gforwards = '/etc/sfwg/forwards.conf'
            gservices = '/etc/sfwg/services.conf'

            if os.path.isfile(gforwards) and os.access(gforwards, os.R_OK):
                print >>sys.stderr, "No forwards file specified, using %s" % (gforwards)
                forwards.append(gforwards)
            if os.path.isfile(gservices) and os.access(gservices, os.R_OK):
                print >>sys.stderr, "No services file specified, using %s" % (gservices)
                services.append(gservices)
            if forwards or services:
                print >>sys.stderr, "A default configuration path has been used - to disable this use --no-find"

        # Parse the configuration files for rules
        try:
            if forwards:
                #fw.enable_nat()
                for path in forwards:
                    parsefile(path, (True, False, False, False), fw.addforward)

            if services:
                for path in services:
                    parsefile(path, (True, False), fw.addservice)
        # Print error for bad configuration lines
        except ConfigError, e:
            print >>sys.stderr, "%s\nin %s at line %s" % (e.message, e.file, e.linenum)
            raise

        try:
            # If a output file is specified, try and write script to it
            if outfile:
                path = os.path.abspath(outfile)
                if os.path.isfile(path):
                    if os.access(path, os.W_OK):
                        print >>sys.stderr, "Warning: file %s exists!" % (path)
                        print >>sys.stderr, "Backing it up to %s.bak" % (path)
                        os.rename(path, path + '.bak')
                        fo = open(path, "w")
                        print >>fo, fw.makescript()
                        fo.close()
                    else:
                        print >>sys.stderr, "You do not have permission to modify %s" % (path)
                elif os.path.isdir(os.path.dirname(path)) and os.access(os.path.dirname(path), os.W_OK):
                    fo = open(path, "w")
                    print >>fo, fw.makescript()
                    fo.close()
                else:
                    print >>sys.stderr, "Could not create %s!" % (path)
                    print >>sys.stderr, "Please check that the file or its parent directory exists and is writable"
            # If no output file, print to stdout
            else:
                print fw.makescript()
            
            # If the execute option was passed, check privileges of the current
            # user then execute the script
            if execute:
                if os.geteuid() == 0:
                    # Do not execute if forwarding rules won't work here
                    if (fw.getopt("nat") or fw.forwards) \
                            and int(commands.getoutput('cat /proc/sys/net/ipv4/ip_forward')) == 0:
                        print >>sys.stderr, "\
You do not have forwarding enabled in your system config but have NAT and/or \n\
forwarding rules enabled.  The generated script will not work on this computer.\n\
Try 'echo 1 > /proc/sys/net/ipv4/ip_forward' to enable it"
                    else:
                        os.system(fw.makescript())
                else:
                    print >>sys.stderr, "Must be root to modify iptables settings"

        # Print any error generated when trying to make the script
        except SFWError, e:
            print >>sys.stderr, e.message
            raise
