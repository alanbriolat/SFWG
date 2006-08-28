#!/usr/bin/python
__author__ = "Alan Briolat <alan@thev0id.net>"
__version__ = "0.1.1"

import getopt, sys, os, commands, string

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

Usage: sfwg [OPTIONS] [OUTFILE]

  -f, --forwards=FILE   Path to file containing port forwarding configuration
  -i, --icmp            Allow ICMP packets on WAN interfaces
  -I, --icmp-rate=COUNT Maximum rate to allow ICMP packets on WAN interfaces
                        (packets per second)
  -l, --lan=IF[,IF...]  All interfaces from which traffic is trusted
  -n, --nat             Use Network Address Translation - automatically enabled
                        if port forwarding is used
      --no-find         Do not check current directory and /etc/sfwg for 
                        services.conf and forwards.conf if not specified
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

shortopts = "f:iI:l:ns:w:x"
longopts = ("forwards=", "icmp", "icmp-rate=", "lan=", "nat", "no-find", \
        "services=", "wan=", "execute", "help", "version")

opts, args = getopt.getopt(sys.argv[1:], shortopts, longopts)

if __name__ == "__main__":
    if ("--help", "") in opts:
        showhelp()
    elif ("--version", "") in opts:
        showversion()
    else:

        forwards = None
        services = None
        outfile = None
        findconfig = True
        execute = False

        fw = SFW()

        for opt, val in opts:
            if opt in ("--forwards", "-f"):
                path = os.path.abspath(val)
                if os.path.isfile(path) and os.access(path, os.R_OK):
                    forwards = path
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
            elif opt in ("--services", "-s"):
                path = os.path.abspath(val)
                if os.path.isfile(path) and os.access(path, os.R_OK):
                    services = path
            elif opt in ("--wan", "-w"):
                fw.wan_interfaces(val)
            elif opt in ("--execute", "-x"):
                execute = True

        if not forwards:
            localconf = os.path.join(os.getcwd(), 'forwards.conf')
            globalconf = '/etc/sfwg/forwards.conf'
            if findconfig and os.path.isfile(localconf) and os.access(localconf, os.R_OK):
                print >>sys.stderr, "forwards.conf not specified but found in current directory, using this instead"
                print >>sys.stderr, "Use --no-find if you do not want to look for a config"
                forwards = localconf
            elif findconfig and os.path.isfile(globalconf) and os.access(globalconf, os.R_OK):
                print >>sys.stderr, "forwards.conf not specified but found in /etc/sfwg, using this instead"
                print >>sys.stderr, "Use --no-find if you do not want to look for a config"
                forwards = globalconf
            else:
                print >>sys.stderr, "No forwards file specified - assuming no forwarding"

        if not services:
            localconf = os.path.join(os.getcwd(), 'services.conf')
            globalconf = '/etc/sfwg/services.conf'
            if findconfig and os.path.isfile(localconf) and os.access(localconf, os.R_OK):
                print >>sys.stderr, "services.conf not specified but found in current directory, using this instead"
                print >>sys.stderr, "Use --no-find if you do not want to look for a config"
                services = localconf
            elif findconfig and os.path.isfile(globalconf) and os.access(globalconf, os.R_OK):
                print >>sys.stderr, "services.conf not specified but found in /etc/sfwg, using this instead"
                print >>sys.stderr, "Use --no-find if you do not want to look for a config"
                services = globalconf
            else:
                print >>sys.stderr, "No services file specified - assuming no WAN-accessible services"

        if not findconfig and not services and not findconfig:
            print >>sys.stderr, "One anally-retentive firewall coming right up!"
            
        try:
            if forwards:
                fw.enable_nat()
                parsefile(forwards, (True, False, False, False), fw.addforward)

            if services:
                parsefile(services, (True, False), fw.addservice)
        except ConfigError, e:
            print >>sys.stderr, "%s\nin %s at line %s" % (e.message, e.file, e.linenum)
            raise

        try:
            if len(args) > 0:
                path = os.path.abspath(args[0])
                if os.path.isfile(path):
                    if os.access(path, os.W_OK):
                        print >>sys.stderr, "Warning: file %s exists!" % (path)
                        print >>sys.stderr, "Backing it up to %s.bak" % (path)
                        os.rename(path, path + '.bak')
                        outfile = open(path, "w")
                        print >>outfile, fw.makescript()
                        outfile.close()
                    else:
                        print >>sys.stderr, "You do not have permission to modify %s" % (path)
                elif os.path.isdir(os.path.dirname(path)) and os.access(os.path.dirname(path), os.W_OK):
                    outfile = open(path, "w")
                    print >>outfile, fw.makescript()
                    outfile.close()
                    
                else:
                    print >>sys.stderr, "Could not create %s!"
                    print >>sys.stderr, "Please check that the file or its parent directory exists and is writable"
            else:
                print fw.makescript()

            if execute:
                if os.geteuid() == 0:
                    #commands.getoutput(fw.makescript())
                    os.system(fw.makescript())
                else:
                    print >>sys.stderr, "Must be root to modify iptables settings"

        except SFWError, e:
            print >>sys.stderr, e.message
            raise
