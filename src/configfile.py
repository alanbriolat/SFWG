#!/usr/bin/python

import os, string

class ConfigFileError:
    def __init__(self, message, file, line):
        self.message = message
        self.file = file
        self.line = line


class ConfigFile:
    def __init__(self, path, keys, splitchar = '|'):
        """
        Get the path to the configuration file, sort out param keys

        path:   path to the config file - will be resolved into an absolute path
        keys:   tuple of dict 'keys' for parameter names - suffixing with ! makes a
                parameter required
        """
        self.path = None
        self.argcount = None
        self.args = []
        self.required_args = []
        self.splitchar = '|'

        #   Check the file exists and is readable
        path = os.path.abspath(path)
        if not os.path.isfile(path):
            raise ConfigFileError("File does not exist", path, 0)
        elif not os.access(path, os.R_OK):
            raise ConfigFileError("File not readable", path, 0)
        else:
            self.path = path

        #   Sort out arg list
        for k in keys:
            if k[len(k) - 1:] == "!":
                k = k.rstrip("!")
                self.args.append(k)
                self.required_args.append(k)
            else:
                self.args.append(k)

        #   Number of args to split into
        self.argcount = len(self.args)

        #   Characted for delimiting fields
        self.splitchar = splitchar


    def getlines(self):
        """
        Get a list of all the lines split into their respective fields

        Throws a ConfigFileError on failure
        """
        #   Initialize an empty list for the parsed lines
        parsed = []
        
        #   Get the lines from the file
        lines = open(self.path, 'r').read().splitlines()
        linenum = 0

        for line in lines:
            #   Keep line number for error messages!
            linenum += 1
            
            #   Strip whitespace from either end
            line = line.strip()
            #   Skip self line if its a comment or empty
            if len(line) == 0 or line[0] == '#':
                continue;
            
            #   Split line into parts
            parts = line.split(self.splitchar, self.argcount - 1)
            #   Error on not enough args
            if len(parts) < self.argcount:
                raise ConfigFileError("Configuration line does not have enough parameters - \
                        expected %s" % self.argcount, self.path, linenum)
                continue
            #   Strip parameters
            parts = [string.strip(p) for p in parts]
            #   Turn into a dict
            parts_dict = dict(zip(self.args, parts))
            #   Check for missing args
            for a in self.required_args:
                if not parts_dict[a]:
                    raise ConfigFileError("Parameter '%s' is required!" % a, self.path, linenum)
            #   No problems - lets add it and go onto the next one!
            parsed.append(parts_dict)

        return parsed
