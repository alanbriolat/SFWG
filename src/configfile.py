#!/usr/bin/python

import os, string

class ConfigError:
    message = None
    linenum = None
    line = None
    requiredargs = None
    def __init__(self, info):
        self.message, self.linenum, self.line, self.requiredargs = info

def parsefile(path, requiredargs, callback = None):
    """
    Parse a configuration file into a list of configuration lines.  Each line is parsed
    into a tuple containing a list of args, and a description

    requiredargs is a tuple specifying both the number of args and if they are
    required, e.g. (True, False, False) means 3 arguments, only the first is required

    Arguments in config files are separated by whitespace, with an empty argument being
    denoted by a '-'

    Example:
        ...
        arg1    -            arg3      # Description
        ...
        
        parsefile('/path/to/file', (True, False, True))
    gives:
        (
            (['arg1', None, 'arg3'], 'Description')
        )

    If a callback function is specified, it will be called with the arg list 
    and the description as the first 2 arguments for each entry
    """
    path = os.path.abspath(path)
    argcount = len(requiredargs)

    if os.path.isfile(path) and os.access(path, os.R_OK):
        
        parsed = []

        # Read the file into a list
        lines = open(path, 'r').read().splitlines()

        l = 0

        for line in lines:
            l += 1

            # Split lines into args and description
            line_split = line.split('#', 1)
            args = line_split[0].strip()
            desc = None
            if len(line_split) > 1:
                desc = line_split[1].strip()

            # If we have some args, process them!
            if args:
                args = string.split(args, maxsplit=(argcount - 1))
                # Error if not enough arguments
                if len(args) < argcount:
                    raise ConfigError, \
                            (("Bad configuration line - not enough arguments", l, line, requiredargs))
                
                # Replace '-' arguments with None
                while args.count('-'):
                    args[args.index('-')] = None

                # Check required args exist
                for i in range(0, argcount):
                    if requiredargs[i] and not args[i]:
                        raise ConfigError, \
                                (("Configuration line does not have required arguments", l, line, requiredargs))
                parsed.append((args, desc))

        if callback:
            for args, desc in parsed:
                callback(args, desc)
        else:
            return parsed

    else:
        raise ConfigError, \
                (("File %s does not exist or is not readable" % (path), 0, None, None))
